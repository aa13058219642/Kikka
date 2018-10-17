#include <iostream>
#include <fstream>
#include <string>
#include <Windows.h>
#include <stdio.h>
using namespace std;


int __stdcall WinMain(HINSTANCE hInstance,
	HINSTANCE hPrevInstance,
	LPTSTR    lpCmdLine,
	int       nCmdShow)
{
	HANDLE hMutex = ::CreateMutex(NULL, FALSE, "Kikka.exe");
	if (GetLastError() == ERROR_ALREADY_EXISTS)
	{
		MessageBox(NULL, "Kikka is Running", "Info", MB_ICONINFORMATION);
		return FALSE;
	}

	fstream fs;
	fs.open("Python\\python.exe", ios::in);
	if (!fs)
	{
		MessageBox(NULL, "Python\\python.exe NOT found", "Error", MB_ICONERROR);
		return -1;
	}
	fs.close();

	fs.open("Main.py", ios::in);
	if (!fs)
	{
		MessageBox(NULL, "Main.py NOT found", "Error", MB_ICONERROR);
		return -1;
	}
	fs.close();

	if (!strcmp(lpCmdLine, "-c"))
	{
		//debug
		system("set PYTHONPATH=Scripts;Scripts/Bin;Scripts/Moudles;Resources; & Python\\python.exe Main.py & pause");
	}
	else
	{
		SetEnvironmentVariable(TEXT("PYTHONPATH"), TEXT("Scripts;Scripts/Bin;Scripts/Moudles;Resources;"));
		TCHAR commandLine[] = TEXT("Python\\python.exe Main.py");
		STARTUPINFO si = { sizeof(si) };
		PROCESS_INFORMATION pi;
		bool bRet = CreateProcess(
			NULL,
			commandLine,
			NULL,
			NULL,
			FALSE,
			CREATE_NO_WINDOW,
			NULL,
			NULL,
			&si,
			&pi);
		WaitForSingleObject(pi.hProcess, INFINITE);
	}
	return 0;
}


