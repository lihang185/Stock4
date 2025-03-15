#include <stdio.h>
#include "L2DayFile.h"


extern "C" __declspec(dllexport)
L2DayFile* l2dayfile_new()
{
	L2DayFile* l2file = new L2DayFile();
	return l2file;
}

extern "C" __declspec(dllexport)
void l2dayfile_del(L2DayFile* obj)
{
	delete obj;
}

extern "C" __declspec(dllexport)
bool l2dayfile_load_file(L2DayFile* obj, char* file_path)
{
	printf("obj:%i, file:%s\n", obj, file_path);
	return  obj->LoadFileAndBuild(file_path);
}


extern "C" __declspec(dllexport)
int l2dayfile_deal_count(L2DayFile* obj)
{
	return obj->deal_count;
}
