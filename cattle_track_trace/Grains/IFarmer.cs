using Orleans;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Grains
{
    public interface IFarmer : IGrainWithGuidKey
    {
        Task<List<Guid>> GetCowIds();
        Task UpdateCows(List<int> cowIds, string newLocation);
    }
}
