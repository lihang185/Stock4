#include <string>
#include <vector>
#include <algorithm>  
#include "BlockManager.h"

class AssertException
{
public:
	const char* file;
	int lineno;
	const char* msg;
	AssertException(const char* _file, int _lineno, const char* _msg) { file = _file; lineno = _lineno; msg = _msg; }
};

#define _ASSERT_PY_ERR(expr, msg) \
            {                                                                                     \
                if(!(expr))                                                                          \
                throw AssertException(__FILE__,__LINE__,msg);												\
            }

struct L2FileItem {
	int time;
	int price;
	int volume;
};

struct WTFileItem {
	int id;
	int buy_orderid;
	int sell_orderid;

	int sell_price;
	int buy_price;

	int buy_volume;
	int sell_volume;
};


struct L2DealInfo {
	int		id;
	int		time;
	bool	is_active_buy;
	int		volume;
	float	price;
	int		buy_id;
	int		buy_flags;
	int		sell_id;
	int		sell_flags;
};

struct L2OrderInfo {
	int		id;
	float	price;
	int		volume;
	int		actual_volume;
	bool	active;
	bool	finished;
	int		deal_count;
	void* deal_list;
};




class L2DayFile {
public:
	L2DayFile();
	~L2DayFile();

	void static_ids(int nDataCount, L2FileItem* l2file_buf, WTFileItem* wtfile_buf);

	int FindBuyId(int id);

	int FindSellId(int id);

	void BuildData(int nDataCount, L2FileItem* l2file_buf, WTFileItem* wtfile_buf);


	bool LoadFile(std::string fullpath, void** out_buf, int* out_len);

	bool LoadFileAndBuild(const char* filepath);


	std::vector<int> buyids;
	std::vector<int> sellids;


	L2FileItem* m_l2file_buf;
	WTFileItem* m_wtfile_buf;

	int deal_count;
	L2DealInfo* deal_list;

	int* buy_list_id2index;
	int* sell_list_id2index;

	BlockManager bm_buy;
	BlockManager bm_sell;
};
