﻿using Grains;
using Microsoft.Extensions.Logging;
using Orleans;
using Orleans.Configuration;
using System;
using System.Threading.Tasks;

namespace Client
{
    class Program
    {
        static int Main(string[] args)
        {
            return RunMainAsync().Result;
        }

        private static async Task<int> RunMainAsync()
        {
            try
            {
                using (var client = await ConnectClient())
                {
                    await DoClientWork(client);
                    Console.ReadKey();
                }
                return 0;
            }
            catch (Exception e)
            {
                Console.WriteLine($"Error: {e.Message}");
                Console.WriteLine("Something went wrong");
                Console.ReadKey();
                return 1;
            }
        }

        private static async Task<IClusterClient> ConnectClient()
        {
            IClusterClient client;
            client = new ClientBuilder()
                .UseLocalhostClustering()
                .Configure<ClusterOptions>(options =>
                {
                    options.ClusterId = "dev";
                    options.ServiceId = "CattleTrackTrace";
                })
                .ConfigureLogging(logging =>
                {
                    logging.AddConsole();
                    logging.SetMinimumLevel(LogLevel.Error);
                })
                .Build();

            await client.Connect();
            Console.WriteLine("Client connected successfully");
            return client;
        }

        private static async Task DoClientWork(IClusterClient client)
        {
            var cow = client.GetGrain<ICow>(Guid.NewGuid());
            Console.WriteLine("Cow grain id: {0}", cow.GetGrainIdentity().IdentityString);

            await cow.UpdateLocation(new Location { Address = "90210 Mooverly Hills", Name = "Moo" });
            
            var cowLocation = await cow.GetLocation();
            Console.WriteLine("Cow address: {0}", cowLocation.Address);
        }
    }
}
