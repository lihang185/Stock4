#ifndef _BLOCK_MANAGER_H
#define _BLOCK_MANAGER_H

#include <algorithm>  
#include <string>
#include <vector>

struct L2OrderInfo;


#define BLOCK_SIZE		4096
#define BLCOK_MASK		0x7F
#define BLCOK_ITEMS		128
#define BLOCK_SHIFT		7
#define ITEM_SHIFT		5
class BlockManager {
public:
	struct block {
		L2OrderInfo* mem_ptr;
		int used;
	};

	BlockManager();
	~BlockManager();

	void NewBlock();
	L2OrderInfo* New();
	int Count();
	L2OrderInfo* Index(int id);

private:
	std::vector<block> m_blocks;
	int m_count;
};


#endif