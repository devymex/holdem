#include <boost/asio.hpp>
#include <iostream>

using boost::asio::ip::tcp;

int main(int argc, char* argv[]) {
	if (argc < 2) {
		return 1;
	}

	const int port = std::atoi(argv[1]);
	
	try{
		boost::asio::io_service io_service;
		tcp::acceptor acceptor(io_service, tcp::endpoint(tcp::v4(), port));
		tcp::socket socket(io_service);

		acceptor.accept(socket);
		boost::asio::streambuf login_buf;
		boost::asio::read_until(socket, login_buf, '\n');

		std::istream is(&login_buf);
		std::string login_name;
		std::getline(is, login_name);
	
		if (login_name.substr(0, 6) == "login ") {
			login_name = login_name.substr(6, -1);
			std::cout << login_name << std::endl;
			return 0;
		}
		else {
			std::cout << "<UNKNOWN>" << std::endl;
			return 1;
		}
	}
	catch (...) {
		std::cout << "<UNKNOWN>" << std::endl;
		return 1;
	}

	return 0;
}
