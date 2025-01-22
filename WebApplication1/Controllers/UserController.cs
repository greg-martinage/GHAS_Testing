using Microsoft.AspNetCore.Mvc;
using System.Data.SqlClient;

namespace VulnerableApp.Controllers
{
    public class UserController : Controller
    {
        public IActionResult Index()
        {
            return View();
        }

        [HttpPost]
        public IActionResult Search(string username)
        {
            string connectionString = "your_connection_string_here";
            string query = "SELECT * FROM Users WHERE Username = '" + username + "'";

            using (SqlConnection connection = new SqlConnection(connectionString))
            {
                connection.Open();
                using (SqlCommand command = new SqlCommand(query, connection))
                {
                    SqlDataReader reader = command.ExecuteReader();
                    while (reader.Read())
                    {
                        ViewBag.Username = reader["Username"];
                        ViewBag.Email = reader["Email"];
                    }
                }
            }

            return View();
        }
    }
}
