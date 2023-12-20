#include "drain_helper.h"
#include <iostream>
namespace npylm{
void trimWstring(std::wstring &ws) {
		// Left trim
		ws.erase(ws.begin(), std::find_if(ws.begin(), ws.end(), [](wchar_t ch) {
			return !std::iswspace(ch);
		}));

		// Right trim
		ws.erase(std::find_if(ws.rbegin(), ws.rend(), [](wchar_t ch) {
			return !std::iswspace(ch);
		}).base(), ws.end());
	}
	std::wstring joinWchar(const wchar_t* wcharArray, int start, int end, wchar_t delimiter) {
		std::wstring result;
		for (int i = start; i <= end; ++i) {
			result += std::to_wstring(wcharArray[i]);
			if (i < end) { // Don't add delimiter after the last character
				result += delimiter;
			}
		}
		return result;
	}
	size_t countSplitChar(const std::wstring& wstr, wchar_t split_char) {
		size_t count = 0;
		for (wchar_t wc : wstr) {
			if (wc == split_char) {
				++count;
			}
		}
		return count;
	}
    wchar_t* split_to_wchars(const std::wstring& str, wchar_t split_char) {
		int sentence_size = countSplitChar(str,split_char)+1;
		wchar_t* tokens = new wchar_t[sentence_size];
		size_t start = 0, end = 0;
		std::wcout<<"splitting "<<str<<std::endl;
		int idx = 0;
		
		while ((end = str.find(split_char, start)) != std::wstring::npos) {
			if (end != start) {
				try {
					tokens[idx++] = std::stoi(str.substr(start, end - start));
					/* code */
				}
				catch(const std::exception& e)
				{
					std::wcerr << "cannot convert " << str.substr(start, end - start)<<'\n';
				}
			}
			start = end + 1;
		}
		if (start < str.length()) {
			try {
					tokens[idx] = std::stoi(str.substr(start));
					/* code */
				}
				catch(const std::exception& e)
				{
					std::wcerr << "cannot convert " << std::stoi(str.substr(start))<<'\n';
				}
			
		}
		
		return tokens;
	}
}