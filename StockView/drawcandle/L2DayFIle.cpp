#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <string>
#include <vector>

#include <algorithm>  

class AssertException
{
public:
	const char* file;
	int lineno;
	const char* msg;
	AssertException(const char* _file, int _lineno, const char* _msg) { file = _file; lineno = _lineno; msg = _msg;}
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

	BlockManager() {
		m_count = 0;
		NewBlock();
	}
	~BlockManager() {
		//printf("delete BlockManager\n");
		std::vector<block>::iterator it;
		for (it = m_blocks.begin(); it != m_blocks.end(); ++it) {
			free(it->mem_ptr);
		}
	}

	void NewBlock() {
		// Create new block
		block newblock;
		newblock.mem_ptr = (L2OrderInfo*)malloc(BLOCK_SIZE);
		newblock.used = 0;
		m_blocks.push_back(newblock);
	}

	L2OrderInfo* New() {
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

	int Count() {
		return m_count;
	}

	L2OrderInfo* Index(int id) {
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

private:
	std::vector<block> m_blocks;
	int m_count;
};

class L2DayFile {
public:
	L2DayFile() {
		deal_list = NULL;

		buy_list_id2index = NULL;
		sell_list_id2index = NULL;
	}
	~L2DayFile() {
		printf("delete L2DayFile\n");
		if (deal_list)
			free(deal_list);
		if (buy_list_id2index)
			free(buy_list_id2index);
		if (sell_list_id2index)
			free(sell_list_id2index);
	}

	std::vector<int> buyids;
	std::vector<int> sellids;
	void static_ids(int nDataCount, L2FileItem* l2file_buf, WTFileItem* wtfile_buf) {

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

	int FindBuyId(int id) {
		int LEN = buyids.size();
		for (int i = 0; i < LEN; i++)
			if (buyids[i] == id)
				return i;
		_ASSERT_PY_ERR(0, "find buy id");
	}

	int FindSellId(int id) {
		int LEN = sellids.size();
		for (int i = 0; i < LEN; i++)
			if (sellids[i] == id)
				return i;
		_ASSERT_PY_ERR(0, "find sellids id");
	}

	void BuildData(int nDataCount, L2FileItem* l2file_buf, WTFileItem* wtfile_buf) {

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


	bool LoadFile(std::string fullpath, void** out_buf, int* out_len) {
		FILE* hf = NULL;
		size_t len;
		void* buf;

		if (fopen_s(&hf, fullpath.c_str(), "rb"))
			return false;

		fseek(hf, 0, SEEK_END);
		len = ftell(hf);
		fseek(hf, 0, SEEK_SET);

		buf = malloc(len);

		fread(buf, 1, len, hf);
		fclose(hf);

		*out_buf = buf;
		*out_len = len;
		return true;
	}

	bool LoadFileAndBuild(const char* filepath) {

		void* l2file_buf = NULL;
		std::string l2file_path = std::string(filepath) + ".L2";
		int l2file_len;

		void* wtfile_buf = NULL;
		int wtfile_len;
		std::string wtfile_path = std::string(filepath) + ".WT";

		if (!LoadFile(l2file_path, &l2file_buf, &l2file_len) || !LoadFile(wtfile_path, &wtfile_buf, &wtfile_len)) {
			if (l2file_buf) free(l2file_buf);
			if (wtfile_buf) free(wtfile_buf);
			return false;
		}

		int dataCount = l2file_len / 12;
		_ASSERT_PY_ERR(dataCount * 12 == l2file_len, "l2file length maybe not correct");
		_ASSERT_PY_ERR(dataCount * 28 == wtfile_len, "wtfile length maybe not correct");

		deal_count = dataCount;
		BuildData(dataCount, (L2FileItem*)l2file_buf, (WTFileItem*)wtfile_buf);

		free(l2file_buf);
		free(wtfile_buf);

		return true;
	}



	L2FileItem* m_l2file_buf;
	WTFileItem* m_wtfile_buf;

	int deal_count;
	L2DealInfo* deal_list;

	int* buy_list_id2index;
	int* sell_list_id2index;

	BlockManager bm_buy;
	BlockManager bm_sell;
};





typedef struct {
	PyObject_HEAD
		L2DayFile* l2file;
} CustomObject;


static int
L2DayFile_init(CustomObject* self, PyObject* args, PyObject* kw) {
	self->l2file = NULL;
	//printf("L2DayFile_init\n");
	return 0;
}

static int
L2DayFile_clear(CustomObject* a) {
	printf("L2DayFile_clear\n");
	return 0;
}

static int
L2DayFile_traverse(CustomObject* o, visitproc visit, void* arg)
{
	return 1;
}

PyObject* L2DayFile_New(PyTypeObject* type, PyObject* args, PyObject* kwds) {
	PyObject* op = type->tp_alloc(type, 0);
	PyObject_GC_Track(op);
	return op;
}


static void L2DayFile_Dealloc(CustomObject* self) {
	//printf("L2DayFile_Dealloc\n");
	if (self->l2file) {
		delete self->l2file;
	}
	Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject*
L2DayFile_DealCount(CustomObject* self)
{
	if (self->l2file) {
		return PyLong_FromLong((int)self->l2file->deal_count);
	}
	else {
		PyErr_Format(PyExc_IndexError, "file not loaded");
		return NULL;
	}
}

static PyObject*
L2DayFile_DealInfo(CustomObject* self, PyObject* args)
{
	int idx;
	if (!PyArg_ParseTuple(args, "i", &idx))
		return NULL;
	if (!self)
		return NULL;

	if(!self->l2file) {
		PyErr_Format(PyExc_IndexError, "file not loaded");
		return NULL;
	}

	L2DayFile* data = self->l2file;

	if (idx < 0 || idx >= self->l2file->deal_count) {
		PyErr_Format(PyExc_IndexError, "deal index out of range", idx);
		return NULL;
	}

	PyObject* rt = PyTuple_New(9);

	PyObject* arg0 = PyLong_FromLong(data->deal_list[idx].id);
	PyTuple_SET_ITEM(rt, 0, arg0);

	PyObject* arg1 = PyLong_FromLong(data->deal_list[idx].time);
	PyTuple_SET_ITEM(rt, 1, arg1);

	PyObject* arg2 = PyBool_FromLong(data->deal_list[idx].is_active_buy);
	PyTuple_SET_ITEM(rt, 2, arg2);

	PyObject* arg3 = PyLong_FromLong(data->deal_list[idx].volume);
	PyTuple_SET_ITEM(rt, 3, arg3);

	PyObject* arg4 = PyFloat_FromDouble(data->deal_list[idx].price);
	PyTuple_SET_ITEM(rt, 4, arg4);

	PyObject* arg5 = PyLong_FromLong(data->deal_list[idx].buy_id);
	PyTuple_SET_ITEM(rt, 5, arg5);

	PyObject* arg6 = PyLong_FromLong(data->deal_list[idx].buy_flags);
	PyTuple_SET_ITEM(rt, 6, arg6);

	PyObject* arg7 = PyLong_FromLong(data->deal_list[idx].sell_id);
	PyTuple_SET_ITEM(rt, 7, arg7);

	PyObject* arg8 = PyLong_FromLong(data->deal_list[idx].sell_flags);
	PyTuple_SET_ITEM(rt, 8, arg8);

/*
	Py_DECREF(arg0);
	Py_DECREF(arg1);
	Py_DECREF(arg2);
	Py_DECREF(arg3);
	Py_DECREF(arg4);
	Py_DECREF(arg5);
	Py_DECREF(arg6);
	Py_DECREF(arg7);
	Py_DECREF(arg8);
*/

	return rt;
}


static PyObject*
L2DayFile_OrderInfo(BlockManager* bm, int index)
{

	L2OrderInfo* data = bm->Index(index);

	PyObject* rt = PyTuple_New(6);

	PyObject* arg0 = PyLong_FromLong(data->id);
	PyTuple_SET_ITEM(rt, 0, arg0);

	PyObject* arg1 = PyFloat_FromDouble(data->price);
	PyTuple_SET_ITEM(rt, 1, arg1);

	PyObject* arg2 = PyLong_FromLong(data->volume);
	PyTuple_SET_ITEM(rt, 2, arg2);

	PyObject* arg3 = PyLong_FromLong(data->actual_volume);
	PyTuple_SET_ITEM(rt, 3, arg3);

	PyObject* arg4 = PyBool_FromLong(data->finished);
	PyTuple_SET_ITEM(rt, 4, arg4);

	PyObject* arg5 = PyLong_FromLong(data->deal_count);
	PyTuple_SET_ITEM(rt, 5, arg5);

	return rt;
}


static PyObject*
L2DayFile_BuyOrderCount(CustomObject* self)
{
	if (!self->l2file) {
		PyErr_Format(PyExc_IndexError, "file not loaded");
		return NULL;
	}
	return PyLong_FromLong((int)self->l2file->bm_buy.Count());
}

static PyObject*
L2DayFile_BuyOrderInfo(CustomObject* self, PyObject* args)
{
	int index;
	if (!PyArg_ParseTuple(args, "i", &index))
		return NULL;
	if (!self)
		return NULL;

	if (!self->l2file) {
		PyErr_Format(PyExc_IndexError, "file not loaded");
		return NULL;
	}
	L2DayFile* data = self->l2file;

	return L2DayFile_OrderInfo(&data->bm_buy, index);
}


static PyObject*
L2DayFile_BuyOrderInfoById(CustomObject* self, PyObject* args)
{
	int order_id;
	if (!PyArg_ParseTuple(args, "i", &order_id))
		return NULL;
	if (!self)
		return NULL;

	if (!self->l2file) {
		PyErr_Format(PyExc_IndexError, "file not loaded");
		return NULL;
	}
	L2DayFile* data = self->l2file;

	int index = data->buy_list_id2index[order_id];

	if (index == -1) {
		PyErr_Format(PyExc_ValueError, "%d is not valid ID", index);
		return NULL;
	}
	else
		return L2DayFile_OrderInfo(&data->bm_buy, index);
}

static PyObject*
L2DayFile_SellOrderCount(CustomObject* self)
{
	if (!self->l2file) {
		PyErr_Format(PyExc_IndexError, "file not loaded");
		return NULL;
	}

	return PyLong_FromLong((int)self->l2file->bm_sell.Count());
}

static PyObject*
L2DayFile_SellOrderInfo(CustomObject* self, PyObject* args)
{
	int index;
	if (!PyArg_ParseTuple(args, "i", &index))
		return NULL;
	if (!self)
		return NULL;

	if (!self->l2file) {
		PyErr_Format(PyExc_IndexError, "file not loaded");
		return NULL;
	}
	L2DayFile* data = self->l2file;

	return L2DayFile_OrderInfo(&data->bm_sell, index);
}



static PyObject*
L2DayFile_SellOrderInfoById(CustomObject* self, PyObject* args)
{
	int order_id;
	if (!PyArg_ParseTuple(args, "i", &order_id))
		return NULL;
	if (!self)
		return NULL;

	if (!self->l2file) {
		PyErr_Format(PyExc_IndexError, "file not loaded");
		return NULL;
	}
	L2DayFile* data = self->l2file;

	int index = data->sell_list_id2index[order_id];

	if (index == -1) {
		PyErr_Format(PyExc_ValueError, "%d is not valid ID", index);
		return NULL;
	}
	else
		return L2DayFile_OrderInfo(&data->bm_sell, index);
}

static PyObject*
L2DayFile_LoadFile(CustomObject* self, PyObject* args)
{
	char* filePath;

	if (!PyArg_ParseTuple(args, "s", &filePath))
		return NULL;


	//printf("L2DayFile_LoadFile: %s\n", filePath);

	try {
		L2DayFile* l2file = new L2DayFile();
		if (l2file->LoadFileAndBuild(filePath)) {
			self->l2file = l2file;
			return PyBool_FromLong(1);
		}
		else {
			PyErr_Format(PyExc_FileExistsError, "file %s is not exist", filePath);
			delete l2file;
			return NULL;
		}
	}
	catch (AssertException e) {
		PyErr_Format(PyExc_AssertionError, "ASSERT %s: %d, %s", e.file, e.lineno, e.msg);
		return NULL;
	}
	/*
	catch (...) {
		PyErr_Format(PyExc_SystemError, "Unknow exception");
		return NULL;
	}
	*/


}

static PyMethodDef list_methods[] = {
	{"LoadFile",	(PyCFunction)L2DayFile_LoadFile,   METH_VARARGS, "LoadFile"},
	{"DealCount",	(PyCFunction)L2DayFile_DealCount,   METH_NOARGS, "get a"},
	{"DealInfo",	(PyCFunction)L2DayFile_DealInfo,   METH_VARARGS, "get a"},
	{"BuyOrderCount",	(PyCFunction)L2DayFile_BuyOrderCount,   METH_NOARGS, "get a"},
	{"BuyOrderInfo",	(PyCFunction)L2DayFile_BuyOrderInfo,   METH_VARARGS, "get a"},
	{"BuyOrderInfoById",	(PyCFunction)L2DayFile_BuyOrderInfoById,   METH_VARARGS, "get a"},
	{"SellOrderCount",	(PyCFunction)L2DayFile_SellOrderCount,   METH_NOARGS, "get a"},
	{"SellOrderInfo",	(PyCFunction)L2DayFile_SellOrderInfo,   METH_VARARGS, "get a"},
	{"SellOrderInfoById",	(PyCFunction)L2DayFile_SellOrderInfoById,   METH_VARARGS, "get a"},

};

PyTypeObject MyType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"L2DayFile",
	sizeof(CustomObject),
	0,
	(destructor)L2DayFile_Dealloc,							/* tp_dealloc */
	0,                                          /* tp_print */
	0,                                          /* tp_getattr */
	0,                                          /* tp_setattr */
	0,                                          /* tp_reserved */
	0,											/* tp_repr */
	0,                                          /* tp_as_number */
	0,                                          /* tp_as_sequence */
	0,                                          /* tp_as_mapping */
	0,                                          /* tp_hash */
	0,                                          /* tp_call */
	0,                                          /* tp_str */
	0,											/* tp_getattro */
	0,                                          /* tp_setattro */
	0,                                          /* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,							/* tp_flags */
	"Custom",									/* tp_doc */
	(traverseproc)L2DayFile_traverse,											/* tp_traverse */
	0,											/* tp_clear */
	0,                                          /* tp_richcompare */
	0,											/* tp_weaklistoffset */
	0,                                          /* tp_iter */
	0,                                          /* tp_iternext */
	list_methods,											/* tp_methods */
	0,											/* tp_members */
	0,											/* tp_getset */
	0,                                          /* tp_base */
	0,                                          /* tp_dict */
	0,                                          /* tp_descr_get */
	0,                                          /* tp_descr_set */
	0,											/* tp_dictoffset */
	(initproc)L2DayFile_init,											/* tp_init */
	0,											/* tp_alloc */
	PyType_GenericNew,								/* tp_new */
	0,											/* tp_free */
	0,                                          /* tp_is_gc */
	0,                                          /* tp_bases */
	0,                                          /* tp_mro */
	0,                                          /* tp_cache */
	0,                                          /* tp_subclasses */
	0,                                          /* tp_weaklist */
	0,                                          /* tp_del */
	0,                                          /* tp_version_tag */
	0,                                          /* tp_finalize */
};

/*
static PyModuleDef custommodule = {
	PyModuleDef_HEAD_INIT,
	.m_name = "custom",
	.m_doc = "Example module that creates an extension type.",
	.m_size = -1,
};
*/