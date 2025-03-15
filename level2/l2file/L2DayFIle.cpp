
#include "BlockManager.h"
#include "L2DayFile.h"




L2DayFile::L2DayFile() {
	m_l2file_buf = NULL;
	m_wtfile_buf = NULL;

	deal_count = 0;
	deal_list = NULL;

	buy_list_id2index = NULL;
	sell_list_id2index = NULL;
}

L2DayFile::~L2DayFile() {
	printf("delete L2DayFile\n");
	if (deal_list)
		free(deal_list);
	if (buy_list_id2index)
		free(buy_list_id2index);
	if (sell_list_id2index)
		free(sell_list_id2index);
	if(m_l2file_buf)
		free(m_l2file_buf);
	if(m_wtfile_buf)
		free(m_wtfile_buf);
}


void L2DayFile::static_ids(int nDataCount, L2FileItem* l2file_buf, WTFileItem* wtfile_buf) {

	for (int i = 0; i < nDataCount; i++) {
		int bid = wtfile_buf[i].buy_orderid;
		int buyorder_id = (bid & 0xFFFFFF) - 1;
		int is_buyorder_begin = bid & 0x40000000;
		if (wtfile_buf[i].buy_orderid & 0x3F000000) {
			int bp = 10;
		}

		if (is_buyorder_begin) {
			buyids.push_back(buyorder_id);
		}

		int sid = wtfile_buf[i].sell_orderid;
		int sellorder_id = (sid & 0xFFFFFF) - 1;
		int is_sellorder_begin = sid & 0x40000000;
		if (wtfile_buf[i].sell_orderid & 0x3F000000) {
			int bp = 10;
		}

		if (is_sellorder_begin) {
			sellids.push_back(sellorder_id);
		}
	}

	std::sort(buyids.begin(), buyids.end());
	std::sort(sellids.begin(), sellids.end());

}

int L2DayFile::FindBuyId(int id) {
	int LEN = buyids.size();
	for (int i = 0; i < LEN; i++)
		if (buyids[i] == id)
			return i;
	int bp = 10;
	_ASSERT_PY_ERR(0, "find buy id");
}

int L2DayFile::FindSellId(int id) {
	int LEN = sellids.size();
	for (int i = 0; i < LEN; i++)
		if (sellids[i] == id)
			return i;
	_ASSERT_PY_ERR(0, "find sellids id");
}

void L2DayFile::BuildData(int nDataCount, L2FileItem* l2file_buf, WTFileItem* wtfile_buf) {

	deal_list = (L2DealInfo*)malloc(sizeof(L2DealInfo) * nDataCount);
	_ASSERT_PY_ERR(deal_list, "malloc failed");
	buy_list_id2index = (int*)malloc(sizeof(int) * nDataCount);
	memset(buy_list_id2index, 0xff, sizeof(int) * nDataCount);
	_ASSERT_PY_ERR(buy_list_id2index, "malloc failed");
	sell_list_id2index = (int*)malloc(sizeof(int) * nDataCount);
	memset(sell_list_id2index, 0xff, sizeof(int) * nDataCount);
	_ASSERT_PY_ERR(sell_list_id2index, "malloc failed");

	static_ids(nDataCount, l2file_buf, wtfile_buf);

	for (int i = 0; i < nDataCount; i++) {
		L2DealInfo* dp = &deal_list[i];
		dp->id = wtfile_buf[i].id;
		dp->time = l2file_buf[i].time;
		dp->price = (float)l2file_buf[i].price / 100.0f;
		dp->volume = l2file_buf[i].volume;
		dp->is_active_buy = true;
		if (dp->volume < 0) {
			dp->is_active_buy = false;
			dp->volume = -dp->volume;
		}

		//===============
		//  Buy Order
		//
		//===============
		int bid = wtfile_buf[i].buy_orderid;
		int buyorder_id = (bid & 0xFFFFFF) - 1;
		int is_buyorder_begin = bid & 0x40000000;
		if(wtfile_buf[i].buy_orderid & 0x3F000000)
			_ASSERT_PY_ERR((wtfile_buf[i].buy_orderid & 0x3F000000) == 0, "buy_orderid & 0x3FFF0000 not empty");
		buyorder_id = FindBuyId(buyorder_id);


		L2OrderInfo* buy_order;
		if (is_buyorder_begin || buyorder_id == dp->id || buy_list_id2index[buyorder_id] == -1) {
			buy_list_id2index[buyorder_id] = bm_buy.Count();
			buy_order = (L2OrderInfo*)bm_buy.New();
			buy_order->id = buyorder_id;
			buy_order->price = dp->price;// (float)wtfile_buf[i].buy_price / 100.0f;
			buy_order->volume = wtfile_buf[i].buy_volume;
			wtfile_buf[i].buy_orderid |= 0x40000000;
		}
		else {
			int index = buy_list_id2index[buyorder_id];
			buy_order = (L2OrderInfo*)bm_buy.Index(index);
			//buy_list_id2index[i] = -1;
		}
		_ASSERT_PY_ERR(buy_order->id == buyorder_id, "buy_order->id != buyorder_id");
		buy_order->actual_volume += dp->volume;
		if (buy_order->volume != wtfile_buf[i].buy_volume)
			buy_order->volume = wtfile_buf[i].buy_volume;
		//_ASSERT_PY_ERR(buy_order->volume == wtfile_buf[i].buy_volume, "buy_order->volume != wtfile_buf[i].buy_volume");

		buy_order->finished = bid & 0x80000000;
		if (buy_order->finished)
			//if (buy_order->actual_volume != buy_order->volume )
			//	_ASSERT_PY_ERR(buy_order->actual_volume == buy_order->volume, "buy_order->actual_volume not finished");
		buy_order->active = dp->is_active_buy;

		buy_order->deal_count++;


		dp->buy_id = buyorder_id;
		dp->buy_flags = (wtfile_buf[i].buy_orderid >> 30 ) & 0x00000003;



		//===============
		//  Sell Order
		//
		//===============
		int sid = wtfile_buf[i].sell_orderid;
		int sellorder_id = (sid & 0xFFFFFF) - 1;
		int is_sellorder_begin = sid & 0x40000000;
		_ASSERT_PY_ERR((wtfile_buf[i].sell_orderid & 0x3F000000) == 0, "sell_orderid & 0x3FFF0000 not empty");
		sellorder_id = FindSellId(sellorder_id);

		L2OrderInfo* sell_order;
		if (is_sellorder_begin || sellorder_id == dp->id || sell_list_id2index[sellorder_id] == -1) {
			sell_list_id2index[sellorder_id] = bm_sell.Count();
			sell_order = (L2OrderInfo*)bm_sell.New();
			sell_order->id = sellorder_id;
			sell_order->price = dp->price;//(float)wtfile_buf[i].sell_price / 100.0f;
			sell_order->volume = wtfile_buf[i].sell_volume;
			wtfile_buf[i].sell_orderid |= 0x40000000;
		}
		else {
			int index = sell_list_id2index[sellorder_id];
			sell_order = (L2OrderInfo*)bm_sell.Index(index);
			//sell_list_id2index[i] = -1;
		}
		_ASSERT_PY_ERR(sell_order->id == sellorder_id, "sell_order->id != sellorder_id");
		sell_order->actual_volume += dp->volume;
		if (sell_order->volume != wtfile_buf[i].sell_volume)
			sell_order->volume = wtfile_buf[i].sell_volume;
		//_ASSERT_PY_ERR(sell_order->volume == wtfile_buf[i].sell_volume, "sell_order->volume != wtfile_buf[i].sell_volume");

		sell_order->finished = sid & 0x80000000;
		if (sell_order->finished)
			//if(sell_order->actual_volume != sell_order->volume)
			//	_ASSERT_PY_ERR(sell_order->actual_volume == sell_order->volume, "sell_order->actual_volume not finished");
		sell_order->active = !dp->is_active_buy;

		sell_order->deal_count++;



		dp->sell_id = sellorder_id;
		dp->sell_flags = (wtfile_buf[i].sell_orderid >> 30) & 0x00000003;
	}

	bool finished = true;
}


bool L2DayFile::LoadFile(std::string fullpath, void** out_buf, int* out_len) {
	FILE* hf = NULL;
	size_t len;
	void* buf;

	if (fopen_s(&hf, fullpath.c_str(), "rb"))
		return false;

	fseek(hf, 0, SEEK_END);
	len = ftell(hf);
	fseek(hf, 0, SEEK_SET);

	buf = malloc(len);
	if (!buf)
		return false;

	fread(buf, 1, len, hf);
	fclose(hf);

	*out_buf = buf;
	*out_len = len;
	return true;
}

bool L2DayFile::LoadFileAndBuild(const char* filepath) {

	std::string l2file_path = std::string(filepath) + ".L2";
	int l2file_len;

	int wtfile_len;
	std::string wtfile_path = std::string(filepath) + ".WT";

	if (!LoadFile(l2file_path, (void**)&m_l2file_buf, &l2file_len)) {
		return false;
	}

	if (!LoadFile(wtfile_path, (void**)&m_wtfile_buf, &wtfile_len)) {
		return false;
	}



	int dataCount = l2file_len / 12;
	_ASSERT_PY_ERR(dataCount * 12 == l2file_len, "l2file length maybe not correct");
	_ASSERT_PY_ERR(dataCount * 28 == wtfile_len, "wtfile length maybe not correct");

	deal_count = dataCount;
	BuildData(dataCount, (L2FileItem*)m_l2file_buf, (WTFileItem*)m_wtfile_buf);

	free(m_l2file_buf);
	m_l2file_buf = NULL;
	free(m_wtfile_buf);
	m_wtfile_buf = NULL;

	return true;
}



