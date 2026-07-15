using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using performance_asp.Data;
using performance_asp.Models;
using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace performance_asp.Controllers
{
    [Route("api/")]
    [ApiController]
    public class FilesController : ControllerBase
    {
        private readonly AppDbContext _context;

        public FilesController(AppDbContext context)
        {
            _context = context;
        }

        // POST: api/files/upload_file
        [HttpPost("upload_file")]
        public async Task<IActionResult> UploadFile(IFormFile file_data)
        {
            if (file_data == null || file_data.Length == 0)
            {
                return BadRequest("No file uploaded.");
            }

            using (var memoryStream = new MemoryStream())
            {
                await file_data.CopyToAsync(memoryStream);
                var fileModel = new FileModel
                {
                    Name = file_data.FileName,
                    FileData = memoryStream.ToArray()
                };

                _context.Files.Add(fileModel);
                await _context.SaveChangesAsync();

                return Ok(new { FileId = fileModel.Id, FileName = fileModel.Name });
            }
        }

        // GET: api/files/download_file/{id}
        [HttpGet("download_file/{id}")]
        public async Task<IActionResult> DownloadFile(int id)
        {
            var file = await _context.Files.FindAsync(id);

            if (file == null)
            {
                return NotFound("File not found.");
            }

            var fileBase64 = Convert.ToBase64String(file.FileData);

            return Ok(new
            {
                FileId = file.Id,
                FileName = file.Name,
                FileData = fileBase64
            });
        }
    }
}
