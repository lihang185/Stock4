
#include <assert.h>
// spam.c
#include "Python.h"


static PyObject* SpamError;

struct ProjData {
	float y_min, y_max;
	int width, height;
	int start_px;
	float zoom;
};

float Project2Py(float value, ProjData* pd)
{
	if( value < 0.1 )
		value = 0.1;
	//float logv = ProjectCoordSystem(value);
	float logv = value;

	float py_inv = (int)((logv - pd->y_min) / (pd->y_max - pd->y_min) * pd->height);
	return pd->height - 1 - py_inv;
}


static PyObject* Func_BuildCandleStickGraphBuffer2(PyObject* self, PyObject* args)
{
	PyObject* data;
	int start_x, end_x;
	float y_min, y_max;
	int view_width, view_height;
	int start_px;
	float zoom;
	int stick_width;
	PyObject* QLineF_class;

	int argCount = PyTuple_Size(args);
	if (!PyArg_ParseTuple(args, "OiiffiiifiO", &data, &start_x, &end_x, &y_min, &y_max, &view_width, &view_height, &start_px, &zoom, &stick_width, &QLineF_class))
		return NULL;

	if (!PyDict_Check(data) || !PyType_Check(QLineF_class))
		return NULL;

	PyTypeObject* typeObj = (PyTypeObject*)QLineF_class;

	PyObject* new_args = PyTuple_New(4);
	PyTuple_SetItem(new_args, 0, PyFloat_FromDouble(0.0));
	PyTuple_SetItem(new_args, 1, PyFloat_FromDouble(0.1));
	PyTuple_SetItem(new_args, 2, PyFloat_FromDouble(1.0));
	PyTuple_SetItem(new_args, 3, PyFloat_FromDouble(2.0));

	PyObject* inst = QLineF_class->ob_type->tp_call(QLineF_class, new_args, NULL);

	//PyObject* inst2 = PyObject_Init(inst, typeObj);
	return inst;
}

inline PyObject* CreateQLineF(PyObject* typeObj, PyObject* lineArgs, float x1, float y1, float x2, float y2) {
	PyTuple_SetItem(lineArgs, 0, PyFloat_FromDouble(x1));
	PyTuple_SetItem(lineArgs, 1, PyFloat_FromDouble(y1));
	PyTuple_SetItem(lineArgs, 2, PyFloat_FromDouble(x2));
	PyTuple_SetItem(lineArgs, 3, PyFloat_FromDouble(y2));

	PyObject* line = typeObj->ob_type->tp_call(typeObj, lineArgs, NULL);
	return line;
}

static PyObject* Func_BuildCandleStickGraphBuffer(PyObject* self, PyObject* args)
{
	PyObject *data;
	int start_x, end_x;
	float y_min, y_max;
	int view_width, view_height;
	int start_px;
	float zoom;
	int stick_width;
	PyObject* QLineF;

	int argCount = PyTuple_Size(args);
	if (!PyArg_ParseTuple(args, "OiiffiiifiO", &data, &start_x, &end_x, &y_min, &y_max, &view_width, &view_height, &start_px, &zoom, &stick_width, &QLineF))
		return NULL;

	if (!PyDict_Check(data) || !PyType_Check(QLineF))
		return NULL;

	ProjData pd;
	pd.y_min = y_min;
	pd.y_max = y_max;
	pd.width = view_width;
	pd.height = view_height;
	pd.start_px = start_px;
	pd.zoom = zoom;


	PyObject *open_list, *high_list, *low_list, *close_list;
	open_list = PyDict_GetItemString(data, "open");
	high_list = PyDict_GetItemString(data, "high");
	low_list = PyDict_GetItemString(data, "low");
	close_list = PyDict_GetItemString(data, "close");
	assert(PyList_Check(open_list));
	assert(PyList_Check(high_list));
	assert(PyList_Check(low_list));
	assert(PyList_Check(close_list));

	PyObject* value = PyList_GET_ITEM(open_list, 0);
	double fvalue = PyFloat_AsDouble(value);

	int c = 0;
	if (stick_width == 1)
		c = 0;
	else if (stick_width == 3)
		c = 1;
	else if (stick_width == 5)
		c = 2;
	else
		c = 3;

	PyObject* red_list = PyList_New(0);
	PyObject* green_list = PyList_New(0);
	PyObject* black_list = PyList_New(0);

	PyObject* lineArgs = PyTuple_New(4);

	for (int i = start_x; i < end_x + 1; i++) {
		float px = i * zoom - start_px;

		float open_v = PyFloat_AsDouble(PyList_GET_ITEM(open_list, i));
		float high_v = PyFloat_AsDouble(PyList_GET_ITEM(high_list, i));
		float low_v = PyFloat_AsDouble(PyList_GET_ITEM(low_list, i));
		float close_v = PyFloat_AsDouble(PyList_GET_ITEM(close_list, i));

		// 判断上涨或下跌
		int type;
		PyObject* list_add_to;
		float diff = close_v - open_v;
		if (diff > 0.009) {
			type = 0;
			list_add_to = red_list;
		}
		else if (diff < -0.009) {
			type = 1;
			list_add_to = green_list;
		}
		else {
			type = 2;
			list_add_to = black_list;
		}

		float yhigh = Project2Py(high_v, &pd);
		float ylow = Project2Py(low_v, &pd);

		PyObject* line;
		
		// 绘制引线
		line = CreateQLineF(QLineF, lineArgs, px + c, ylow, px + c, yhigh); PyList_Append(list_add_to, line); Py_DECREF(line);

		// 绘制块
		if (stick_width == 1) {
			// 不处理
		}
		else {
			float yopen = Project2Py(open_v, &pd);
			float yclose = Project2Py(close_v, &pd);

			if (type == 2) {
				line = CreateQLineF(QLineF, lineArgs, px, yclose, px+stick_width, yclose); PyList_Append(list_add_to, line); Py_DECREF(line);
			}
			else
				for( int j=0; j< stick_width; j++ )
					if (j != c) {
						line = CreateQLineF(QLineF, lineArgs, px+j, yopen, px+j, yclose); PyList_Append(list_add_to, line); Py_DECREF(line);
					}
		}
	}



	PyObject* listTuple = PyTuple_New(3);
	PyTuple_SetItem(listTuple, 0, red_list);
	PyTuple_SetItem(listTuple, 1, green_list);
	PyTuple_SetItem(listTuple, 2, black_list);

	return listTuple;
}

static PyMethodDef SpamMethods[] = {
	{"BuildCandleStickGraphBuffer",  Func_BuildCandleStickGraphBuffer, METH_VARARGS, "Draw Candle Graph"},
	{NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef draw_candle_mmodule = {
	PyModuleDef_HEAD_INIT,
	"drawcandle",   /* name of module */
	"hahaha~~~~", /* module documentation, may be NULL */
	-1,       /* size of per-interpreter state of the module,
				 or -1 if the module keeps state in global variables. */
	SpamMethods
};

extern PyTypeObject MyType;

PyMODINIT_FUNC
PyInit_drawcandle(void)
{
	PyObject* m;

	m = PyModule_Create(&draw_candle_mmodule);
	if (m == NULL)
		return NULL;

	SpamError = PyErr_NewException("spam.error", NULL, NULL);
	Py_XINCREF(SpamError);
	if (PyModule_AddObject(m, "error", SpamError) < 0) {
		Py_XDECREF(SpamError);
		Py_CLEAR(SpamError);
		Py_DECREF(m);
		return NULL;
	}

	if (PyType_Ready(&MyType) < 0)
		return NULL;

	if (PyModule_AddObject(m, "L2DayFile", (PyObject*)& MyType) < 0) {
		Py_XDECREF(&MyType);
		Py_DECREF(m);
		return NULL;
	}

	return m;
}