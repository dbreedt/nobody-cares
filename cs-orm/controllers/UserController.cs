using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using csorm.Data;
using csorm.Models;

namespace csorm.Controllers;

[ApiController]
[Route("/user")]
public class UserController : ControllerBase
{
    private readonly UserContext _context;

    public UserController(UserContext context)
    {
        _context = context;
    }

    [HttpGet("{id:long}")]
    public async Task<IActionResult> GetUser(long id)
    {
        var user = await _context.User.FindAsync(id);
        if (user == null)
            return NotFound();

        return Ok(new UserResponse(user));
    }
}
