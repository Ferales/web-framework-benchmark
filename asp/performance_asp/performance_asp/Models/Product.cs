using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace performance_asp.Models
{
    public class Product
    {
        [Key]
        [Column("id")]
        public int Id { get; set; }

        [Required]
        [StringLength(100)]
        [Column("name")]
        public string Name { get; set; }

        [Required]
        [Column("price")]
        public double Price { get; set; }

        [Required]
        [Column("stock")]
        public int Stock { get; set; }

        public virtual ICollection<OrderProduct> OrderProducts { get; set; }
    }
}
