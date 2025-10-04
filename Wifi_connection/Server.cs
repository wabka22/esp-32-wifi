using System.Net;
using System.Net.Sockets;
using System.Text;

class Server
{
    private const int PORT = 8888;
    private static bool ledState = false;

    static void Main()
    {
        StartServer();
    }

    static void StartServer()
    {
        TcpListener server = new TcpListener(IPAddress.Any, PORT);
        server.Start();
        Console.WriteLine($"Server started on {GetLocalIPAddress()}:{PORT}");

        while (true)
        {
            TcpClient client = server.AcceptTcpClient();
            Console.WriteLine($"Client connected: {((IPEndPoint)client.Client.RemoteEndPoint).Address}");

            _ = Task.Run(() => ProcessClient(client)); 
        }
    }

    static void ProcessClient(TcpClient client)
    {
        try
        {
            using NetworkStream stream = client.GetStream();
            using StreamReader reader = new StreamReader(stream, Encoding.UTF8);
            using StreamWriter writer = new StreamWriter(stream, Encoding.UTF8) { AutoFlush = true };

            string? received = reader.ReadLine();
            if (received != null)
            {
                Console.WriteLine($"Received: {received}");

                ledState = !ledState;
                string response = $"LED state: {(ledState ? "ON" : "OFF")}";
                writer.WriteLine(response);

                Console.WriteLine($"Sent: {response}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
        finally
        {
            client.Close();
            Console.WriteLine("Client disconnected\n");
        }
    }

    static string GetLocalIPAddress()
    {
        foreach (var ip in Dns.GetHostEntry(Dns.GetHostName()).AddressList)
        {
            if (ip.AddressFamily == AddressFamily.InterNetwork)
                return ip.ToString();
        }
        return "Unknown";
    }
}
