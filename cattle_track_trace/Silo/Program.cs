using Grains;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Orleans;
using Orleans.Configuration;
using Orleans.Hosting;
using Orleans.Storage;
using System;
using System.Threading.Tasks;
using System.IO;
using Orleans.Runtime;

namespace Silo
{
    class Program
    {
        static int Main(string[] args)
        {
            Console.WriteLine("Main running");
            return RunTaskAsync().Result;
        }

        private static async Task<int> RunTaskAsync()
        {
            try
            {
                Console.WriteLine("Starting silo");
                var host = await StartSiloAsync();
                Console.WriteLine("Silo created. Press any key to stop");
                Console.ReadLine();
                var database = host.Services.GetService<FileDatabaseInterface>();
                database.Dispose();
                await host.StopAsync();
                Console.WriteLine("Returning 0");
                return 0;
            }
            catch (Exception e)
            {
                Console.WriteLine(e);
                return 1;
            }
        }

        private static async Task<ISiloHost> StartSiloAsync()
        {
            var builder = new SiloHostBuilder()
                .UseLocalhostClustering()
                .Configure<ClusterOptions>(options =>
                {
                    options.ClusterId = "dev";
                    options.ServiceId = "CattleTrackTrace";
                })
                .ConfigureServices(services =>
                {
                    services.AddSingleton(new FileDatabaseInterfaceOptions
                    {
                        DatabaseScript = "C:\\Users\\traff\\Documents\\repos\\bsc\\bsc-code\\cattle_track_trace\\Database\\run-file-database.py",
                        ComponentName = "component",
                        DataDirectory = "C:\\Users\\traff\\Documents\\repos\\bsc\\bsc-code\\cattle_track_trace\\Database\\data",
                    });
                    services.AddSingletonNamedService<IGrainStorage, FileDatabaseInterface>("FileStorage");
                })
                .ConfigureApplicationParts(parts =>
                {
                    parts.AddApplicationPart(typeof(Cow).Assembly).WithReferences();
                })
                .ConfigureLogging(logging => {
                    logging.AddConsole();
                    logging.SetMinimumLevel(LogLevel.Warning);
                });

            var host = builder.Build();
            await host.StartAsync();
            return host;
        }
    }
}
