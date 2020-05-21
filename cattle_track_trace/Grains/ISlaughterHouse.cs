using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace Grains
{
    public interface ISlaughterHouse
    {
        Task<List<int>> GetCowIds();
        Task<List<int>> GetMeatCutIds();
        Task<int> ProduceMeatCut(int cowId);
    }
}
