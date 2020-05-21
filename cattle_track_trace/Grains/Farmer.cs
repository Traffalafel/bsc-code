using Orleans;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Grains
{
    public class Farmer : Grain, IFarmer
    {

        public Task<List<Guid>> GetCowIds()
        {
            throw new NotImplementedException();
        }

        public Task UpdateCows(List<int> cowIds, string newLocation)
        {
            throw new NotImplementedException();
        }
    }
}
