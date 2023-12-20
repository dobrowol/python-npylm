#pragma once
#include <string>
#include <algorithm>
#include <cwctype>

namespace npylm{
	void trimWstring(std::wstring &ws);
	std::wstring joinWchar(const wchar_t* wcharArray, int start, int end, wchar_t delimiter);
	size_t countSplitChar(const std::wstring& wstr,wchar_t split_char);
    wchar_t* split_to_wchars(const std::wstring& str, wchar_t split_char=L' ');
}