//! Shared memory (SHM) buffer allocation and pixel manipulation.
#![deny(unsafe_code)]

use crate::error::{ShellError, ShellResult};
use crate::wayland::protocols::ShellWaylandState;
use std::io::{Seek, SeekFrom, Write};
use std::os::unix::io::AsFd;
use wayland_client::protocol::{
    wl_buffer::WlBuffer,
    wl_shm::{Format as ShmFormat, WlShm},
    wl_shm_pool::WlShmPool,
};
use wayland_client::QueueHandle;

/// Encapsulates a shared memory backing file and corresponding Wayland pool/buffer.
#[derive(Debug)]
pub struct ShmBuffer {
    pub file: std::fs::File,
    pub pool: WlShmPool,
    pub buffer: WlBuffer,
    pub width: u32,
    pub height: u32,
    pub stride: u32,
}

impl ShmBuffer {
    /// Allocate an anonymous tempfile backed SHM buffer in ARGB8888 format.
    pub fn allocate(
        shm: &WlShm,
        qh: &QueueHandle<ShellWaylandState>,
        width: u32,
        height: u32,
    ) -> ShellResult<Self> {
        if width == 0 || height == 0 {
            return Err(ShellError::ShmError(format!(
                "Invalid buffer dimensions: {width}x{height}"
            )));
        }

        let stride = width * 4;
        let size = (stride * height) as usize;

        let mut file = tempfile::tempfile().map_err(|e| {
            ShellError::ShmError(format!("Failed to allocate temporary shm file: {e}"))
        })?;

        file.set_len(size as u64)
            .map_err(|e| ShellError::ShmError(format!("Failed to set SHM buffer size: {e}")))?;

        // Fill initially with transparent black
        let zero_page = vec![0u8; size];
        file.seek(SeekFrom::Start(0))?;
        file.write_all(&zero_page)?;
        file.flush()?;

        let pool = shm.create_pool(file.as_fd(), size as i32, qh, ());
        let buffer = pool.create_buffer(
            0,
            width as i32,
            height as i32,
            stride as i32,
            ShmFormat::Argb8888,
            qh,
            (),
        );

        Ok(Self {
            file,
            pool,
            buffer,
            width,
            height,
            stride,
        })
    }

    /// Write raw ARGB8888 bytes into the backing file.
    pub fn write_pixels(&mut self, data: &[u8]) -> ShellResult<()> {
        let expected_len = (self.stride * self.height) as usize;
        if data.len() != expected_len {
            return Err(ShellError::ShmError(format!(
                "Pixel buffer length mismatch: expected {}, got {}",
                expected_len,
                data.len()
            )));
        }

        self.file.seek(SeekFrom::Start(0))?;
        self.file.write_all(data)?;
        self.file.flush()?;
        Ok(())
    }

    /// Destroy the Wayland buffer and pool resources.
    pub fn destroy(self) {
        self.buffer.destroy();
        self.pool.destroy();
    }
}
