using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using performance_asp.Data;
using performance_asp.Models;

namespace performance_asp.Controllers
{
    [Route("api")]
    [ApiController]
    public class OrdersController : ControllerBase
    {
        private readonly AppDbContext _context;

        public OrdersController(AppDbContext context)
        {
            _context = context;
        }

        // 3. Get user orders within a date range with status filter
        [HttpGet("orders")]
        public async Task<ActionResult<IEnumerable<Order>>> GetOrders(
            [FromQuery] int userId,
            [FromQuery] DateTime startDate,
            [FromQuery] DateTime endDate,
            [FromQuery] string status = "Pending")
        {
            // Validate status
            string[] validStatuses = { "Pending", "Completed", "Cancelled" };
            if (!validStatuses.Contains(status))
            {
                return BadRequest(new { error = "Invalid order status" });
            }

            if (userId == 0 || startDate == default || endDate == default)
            {
                return BadRequest(new { error = "Required parameters: userId, startDate, endDate" });
            }

            try
            {
                var orders = await _context.Orders
                    .Where(o => o.UserId == userId &&
                                o.OrderDate >= startDate &&
                                o.OrderDate <= endDate &&
                                o.Status == status)
                    .Include(o => o.OrderProducts)
                        .ThenInclude(op => op.Product)
                    .ToListAsync();

                return Ok(orders);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = "Error retrieving user orders", details = ex.Message });
            }
        }
    }
}