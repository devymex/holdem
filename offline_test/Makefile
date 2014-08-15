
.PHONY: clean

get_login_name: get_login_name.cpp
	g++ -std=c++11 -o get_login_name get_login_name.cpp -lpthread -lboost_system

get_login_name.exe: get_login_name.cpp
	g++ -std=c++11 -o get_login_name -D_WIN32_WINNT=0x0601 get_login_name.cpp -lws2_32 -lmswsock -l:libboost_system-mgw48-mt-1_55.a

clean:
	rm -f get_login_name
	rm -f get_login_name.exe
