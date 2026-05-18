using Microsoft.EntityFrameworkCore;
using csorm.Data;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddDbContext<UserContext>(options =>
    options.UseNpgsql(
        builder.Configuration.GetConnectionString("DefaultConnection"))
        .LogTo(Console.WriteLine, LogLevel.Warning)
        );
builder.Services.AddControllers();

var app = builder.Build();

app.Urls.Add("http://0.0.0.0:8080");

// Configure the HTTP request pipeline.
app.MapControllers();
app.Run();