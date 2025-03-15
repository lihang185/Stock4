

######################
#   Block optimization strategy
# 
# Qt直接绘制大量图元会导致极低的
# 性能，把图元绘制到Block缓存单元
# 避免循环中执行大量Python代码
# 是很好的优化策略
#
######################
class BlockManager:
    BLOCK_SIZE_SHIFT = 7
    class Block: pass
    
    def __init__(self,  LEN):
        self.list = []
        
        BLOCK_SIZE = 1<<BlockManager.BLOCK_SIZE_SHIFT
        
        for i in range(0,  LEN,  BLOCK_SIZE ) :
            start_x = i
            end_x = i + BLOCK_SIZE
            if end_x > LEN:
                end_x = LEN
                
            block = BlockManager.Block()
            block.start_x = start_x
            block.end_x = end_x
            self.list.append(block)
            
    def blocks(self, start_x,  end_x):
        start_block =  start_x >> BlockManager.BLOCK_SIZE_SHIFT
        end_block =  (end_x >> BlockManager.BLOCK_SIZE_SHIFT)+1
        # 分片返回性能如何 ？？
        return self.list[start_block:end_block]
            
