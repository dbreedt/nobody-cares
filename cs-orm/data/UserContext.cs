using Microsoft.EntityFrameworkCore;
using csorm.Models;

namespace csorm.Data;

public class UserContext : DbContext
{
    public UserContext(DbContextOptions<UserContext> options) : base(options) { }

    public DbSet<User> User { get; set; }
}
