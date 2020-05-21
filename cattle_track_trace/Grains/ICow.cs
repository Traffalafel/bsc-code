using Orleans;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Grains
{
    public interface ICow : IGrainWithGuidKey
    {
        Task<Guid> GetOwnerId();
        Task SetOwnerId(Guid newOwnerId);

        Task<Location> GetLocation();
        Task UpdateLocation(Location newLocation);

        Task<List<Point>> GetTrajectory();
        Task UpdateTrajectory(Point newPosition);
    }
}
