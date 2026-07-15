using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using performance_asp.Models;
using performance_asp.Data;

namespace performance_asp.Controllers
{
    [Route("api")]
    [ApiController]
    public class ProductsController : ControllerBase
    {
        private readonly AppDbContext _context;

        public ProductsController(AppDbContext context)
        {
            _context = context;
        }

        // 1. Get cheapest/most expensive products with pagination
        [HttpGet("products")]
        public async Task<ActionResult<IEnumerable<Product>>> GetProducts(
            [FromQuery] int limit = 10,
            [FromQuery] int offset = 0,
            [FromQuery] string direction = "ASC")
        {
            try
            {
                var query = _context.Products.AsQueryable();

                if (direction.ToUpper() == "DESC")
                {
                    query = query.OrderByDescending(p => p.Price);
                }
                else
                {
                    query = query.OrderBy(p => p.Price);
                }

                var products = await query
                    .Skip(offset)
                    .Take(limit)
                    .ToListAsync();

                return Ok(products);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = "Error retrieving products", details = ex.Message });
            }
        }

        // 2. Get 10 most popular products based on order quantity
        [HttpGet("popular")]
        public async Task<ActionResult<IEnumerable<object>>> GetPopularProductsWithSql()
        {
            try
            {
                using (var connection = _context.Database.GetDbConnection())
                {
                    await connection.OpenAsync();
                    using (var command = connection.CreateCommand())
                    {
                        command.CommandText = @"
                    SELECT 
                        p.id,
                        p.name,
                        p.price,
                        COALESCE(SUM(op.quantity), 0) as total_quantity
                    FROM 
                        products p
                    LEFT JOIN 
                        order_products op ON p.id = op.product_id
                    GROUP BY 
                        p.id, p.name, p.price
                    ORDER BY 
                        total_quantity DESC
                    LIMIT 10";

                        using (var reader = await command.ExecuteReaderAsync())
                        {
                            var results = new List<object>();
                            while (await reader.ReadAsync())
                            {
                                results.Add(new
                                {
                                    Id = reader.GetInt32(0),
                                    Name = reader.GetString(1),
                                    Price = reader.GetDecimal(2),
                                    TotalQuantity = reader.GetInt32(3)
                                });
                            }
                            return Ok(results);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Detailed error: {ex}");
                return StatusCode(500, new { error = "Error fetching popular products", details = ex.Message });
            }
        }
    }
}