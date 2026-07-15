using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace performance_asp.Models
{
    [Table("files")]
    public class FileModel
    {
        [Key]
        [Column("id")]
        public int Id { get; set; }

        [Column("file_data")]
        public byte[] FileData { get; set; }

        [Column("name")]
        public string Name { get; set; }
    }
}