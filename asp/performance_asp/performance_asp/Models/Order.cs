using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace performance_asp.Models
{
    public class Order
    {
        [Key]
        [Column("id")]
        public int Id { get; set; }

        [Required]
        [ForeignKey("User")]
        [Column("user_id")]
        public int UserId { get; set; }

        [Required]
        [Column("order_date")]
        public DateTime OrderDate { get; set; }

        [Required]
        [DefaultValue("Pending")]
        [Column("status")]
        public string Status { get; set; }

        public virtual ICollection<OrderProduct> OrderProducts { get; set; }
    }
}
