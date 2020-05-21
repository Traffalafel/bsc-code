using Orleans;
using Orleans.Providers;
using Orleans.Runtime;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Grains
{
    [StorageProvider(ProviderName = "FileStorage")]
    public class Cow : Grain, ICow
    {
        private IPersistentState<Guid> _ownerId;
        private IPersistentState<Location> _location;
        private IPersistentState<List<Point>> _trajectory;

        public Cow(
            [PersistentState("CowOwnerId", "FileStorage")] IPersistentState<Guid> ownerId,
            [PersistentState("CowLocation", "FileStorage")] IPersistentState<Location> location,
            [PersistentState("CowItinerary", "FileStorage")] IPersistentState<List<Point>> trajectory)
        {
            _trajectory = trajectory;
            _ownerId = ownerId;
            _location = location;
        }

        public override async Task OnActivateAsync()
        {
            await base.OnActivateAsync();

            if (_ownerId.State == null)
            {
                _ownerId.State = Guid.Empty;
            }
            if (_location.State == null)
            {
                _location.State = new Location { Address = null, Name = null };
            }
            if (_trajectory.State == null)
            {
                _trajectory.State = new List<Point>();
            }
        }

        public Task<Guid> GetOwnerId()
        {
            return Task.FromResult(_ownerId.State);
        }

        public Task SetOwnerId(Guid newOwnerId)
        {
            _ownerId.State = newOwnerId;
            return _ownerId.WriteStateAsync();
        }

        public Task<Location> GetLocation()
        {
            Console.WriteLine("Location wrapper: {0}", _location);  
            return Task.FromResult(_location.State);
        }
        public Task UpdateLocation(Location newLocation)
        {
            _location.State = newLocation;
            return _location.WriteStateAsync();
        }

        public Task<List<Point>> GetTrajectory()
        {
            return Task.FromResult(_trajectory.State);
        }

        public async Task UpdateTrajectory(Point newPosition)
        {
            _trajectory.State.Add(newPosition);
            await _trajectory.WriteStateAsync();
        }
    }
}
