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

	fs.open("PYTHONPATH", ios::in);
	string pythonpath = "";
	if (fs)
	{
		while (!fs.eof())
		{
			char buf[1024];
			fs.getline(buf, 1024);
			pythonpath += buf;
		}
	}
	else
	{
		pythonpath = "Scripts;Scripts/Bin;Scripts/Moudles;Scripts/Command;Scripts/Ghost;Resources;";
	}
	fs.close();

	if (!strcmp(lpCmdLine, "-c"))
	{
		//debug
		string cmd = "set PYTHONPATH=";
		cmd += pythonpath;
		cmd += " & Python\\python.exe Main.py";
		cmd += " & pause";
		system(cmd.c_str());
	}
	else
	{
		SetEnvironmentVariable(TEXT("PYTHONPATH"), TEXT(pythonpath.c_str()));
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


