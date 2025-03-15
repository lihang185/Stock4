#include "BlockManager.h"
#include "L2DayFile.h"


BlockManager::BlockManager() {
	m_count = 0;
	NewBlock();
}

BlockManager::~BlockManager() {
	//printf("delete BlockManager\n");
	std::vector<block>::iterator it;
	for (it = m_blocks.begin(); it != m_blocks.end(); ++it) {
		free(it->mem_ptr);
	}
}

void BlockManager::NewBlock() {
	// Create new block
	block newblock;
	newblock.mem_ptr = (L2OrderInfo*)malloc(BLOCK_SIZE);
	newblock.used = 0;
	m_blocks.push_back(newblock);
}

L2OrderInfo* BlockManager::New() {
	block* end = &m_blocks.back();
	if (end->used >= BLCOK_ITEMS) {
		NewBlock();
		end = &m_blocks.back();
	}

	m_count++;
	L2OrderInfo* ptr = end->mem_ptr + end->used;
	memset(ptr, 0, sizeof(L2OrderInfo));
	end->used++;
	return ptr;
}

int BlockManager::Count() {
	return m_count;
}

L2OrderInfo* BlockManager::Index(int id) {
	_ASSERT(id >= 0 && id < m_count);
	if (id == -1) {
		int bp = 0;
	}

	int block_id = id >> BLOCK_SHIFT;
	L2OrderInfo* block_ptr = m_blocks[block_id].mem_ptr;

	int item_id = (id & BLCOK_MASK);

	L2OrderInfo* ptr = block_ptr + item_id;
	return ptr;
}