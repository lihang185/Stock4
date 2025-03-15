#define Py_LIMITED_API

#include <Python.h>
#include "BlockManager.h"
#include "L2DayFile.h"



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
	PyObject* op = PyType_GenericNew(type, args, kwds);
	PyObject_GC_Track(op);
	return op;
}


static void L2DayFile_Dealloc(CustomObject* self) {
	//printf("L2DayFile_Dealloc\n");
	if (self->l2file) {
		delete self->l2file;
	}
	_Py_Dealloc(&self->ob_base);
	//Py_TYPE(self)->tp_free((PyObject*)self);
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

	if (!self->l2file) {
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
	PyTuple_SetItem(rt, 0, arg0);

	PyObject* arg1 = PyLong_FromLong(data->deal_list[idx].time);
	PyTuple_SetItem(rt, 1, arg1);

	PyObject* arg2 = PyBool_FromLong(data->deal_list[idx].is_active_buy);
	PyTuple_SetItem(rt, 2, arg2);

	PyObject* arg3 = PyLong_FromLong(data->deal_list[idx].volume);
	PyTuple_SetItem(rt, 3, arg3);

	PyObject* arg4 = PyFloat_FromDouble(data->deal_list[idx].price);
	PyTuple_SetItem(rt, 4, arg4);

	PyObject* arg5 = PyLong_FromLong(data->deal_list[idx].buy_id);
	PyTuple_SetItem(rt, 5, arg5);

	PyObject* arg6 = PyLong_FromLong(data->deal_list[idx].buy_flags);
	PyTuple_SetItem(rt, 6, arg6);

	PyObject* arg7 = PyLong_FromLong(data->deal_list[idx].sell_id);
	PyTuple_SetItem(rt, 7, arg7);

	PyObject* arg8 = PyLong_FromLong(data->deal_list[idx].sell_flags);
	PyTuple_SetItem(rt, 8, arg8);

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
	PyTuple_SetItem(rt, 0, arg0);

	PyObject* arg1 = PyFloat_FromDouble(data->price);
	PyTuple_SetItem(rt, 1, arg1);

	PyObject* arg2 = PyLong_FromLong(data->volume);
	PyTuple_SetItem(rt, 2, arg2);

	PyObject* arg3 = PyLong_FromLong(data->actual_volume);
	PyTuple_SetItem(rt, 3, arg3);

	PyObject* arg4 = PyBool_FromLong(data->finished);
	PyTuple_SetItem(rt, 4, arg4);

	PyObject* arg5 = PyLong_FromLong(data->deal_count);
	PyTuple_SetItem(rt, 5, arg5);

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
			//PyErr_Format(PyExc_FileExistsError, "file %s is not exist", filePath);
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
	{NULL,NULL,NULL,NULL}
};

#if 0
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
#endif

static PyType_Slot MyClass_slots[] = {
	{Py_tp_new, (void*)PyType_GenericNew},
	{Py_tp_init, (void*)L2DayFile_init},
	{Py_tp_dealloc, (void*)L2DayFile_Dealloc},
	{Py_tp_methods, (void*)list_methods},
	{0, 0}
};


static PyType_Spec spec_myclass = {
"L2DayFile", // name
sizeof(CustomObject), // basicsize
0, // itemsize
Py_TPFLAGS_DEFAULT, // flags
MyClass_slots // slots
};


static PyObject* test(PyObject* self, PyObject* args)
{
	return NULL;
}

static PyMethodDef l2file_Methods[] = {
	{"test",  test, METH_VARARGS, "test"},
	{NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef l2file_module = {
	PyModuleDef_HEAD_INIT,
	"l2file",   /* name of module */
	"hahaha~~~~", /* module documentation, may be NULL */
	-1,       /* size of per-interpreter state of the module,
				 or -1 if the module keeps state in global variables. */
	l2file_Methods
};

static PyObject* l2fileError;

PyMODINIT_FUNC
PyInit_l2file(void)
{
	PyObject* m;

	m = PyModule_Create(&l2file_module);
	if (m == NULL)
		return NULL;

	l2fileError = PyErr_NewException("spam.error", NULL, NULL);
	Py_XINCREF(l2fileError);
	if (PyModule_AddObject(m, "error", l2fileError) < 0) {
		Py_XDECREF(l2fileError);
		Py_CLEAR(l2fileError);
		Py_DECREF(m);
		return NULL;
	}

	PyObject* myclass = PyType_FromSpec(&spec_myclass);
	if (myclass == NULL)
		return NULL;

	Py_INCREF(myclass);

	int ret = PyType_Ready(Py_TYPE(myclass));

	if (PyObject_TypeCheck(Py_TYPE(myclass), &PyBaseObject_Type))
		ret = 0;

	if (PyModule_AddObject(m, "L2DayFile", myclass) < 0) {
		Py_XDECREF(myclass);
		Py_DECREF(m);
		return NULL;
	}


	return m;
}

