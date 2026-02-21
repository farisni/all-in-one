# Created by nidazhong at 2026/02/02 23:39
# leetgo: 1.4.16
# https://leetcode.cn/problems/two-sum/

from typing import *
from leetgo_py import *

# @lc code=begin

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        map = {}
        for i,val in enumerate(nums):
            if ((target - val) in map):
                return [map[target - val], i]
            map[val] = i
        return []
        

# @lc code=end

if __name__ == "__main__":
    nums: List[int] = deserialize("List[int]", read_line())
    target: int = deserialize("int", read_line())
    ans = Solution().twoSum(nums, target)
    print("\noutput:", serialize(ans, "integer[]"))
