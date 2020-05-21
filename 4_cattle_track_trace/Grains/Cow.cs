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
        }

        public override async Task OnActivateAsync()
        {
            await base.OnActivateAsync();
            if (_trajectory.State == null)
            {
                // Default state is empty list
                _ownerId = null;
                _location = null;
                _trajectory.State = new List<Point>();
            }
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
