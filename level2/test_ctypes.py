import ctypes

l2file_dll = ctypes.CDLL('./l2file.pyd')

obj = l2file_dll.l2dayfile_new()

ret =l2file_dll.l2dayfile_load_file(ctypes.c_void_p(obj),  ctypes.c_char_p(str("C:/proj/Stock4/test/000058").encode()) )

count = l2file_dll.l2dayfile_deal_count(ctypes.c_void_p(obj))

print('deal_count:',  count)
