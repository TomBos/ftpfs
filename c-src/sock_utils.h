#ifndef SOCK_UTILS_H
#define SOCK_UTILS_H

#include <time.h>
#include <sys/time.h>
#include <sys/socket.h>

#define BUFFER_SIZE 1024

#include "validate.h"

// Fill in current timestamp into the context (e.g. "[28.07.2025 19:21:52]")
void generate_timestamp(SocketContext *pctx) {
	// get current time (seconds and microseconds since epoch)
	struct timeval tv;
	gettimeofday(&tv, NULL);

	// convert seconds part to local broken-down time
	struct tm *pt = localtime(&tv.tv_sec);
	
	// format the time if it exists
	if (!pt) return;
	char base[sizeof(pctx->timestamp)];
	strftime(base, sizeof(base), "[%d.%m.%Y %H:%M:%S", pt);

	// append milliseconds
	snprintf(pctx->timestamp, sizeof(pctx->timestamp), "%s.%03ld]", base, tv.tv_usec / 1000);
}

// Create a TCP socket, retrying if needed
int create_tcp_socket(SocketContext *pctx) {
	// start with explicitely invalid socket
	// prevents reuse of invalid sockets	
	pctx->sockfd = -1;

	// get max number of tries in local copy
	int retries = pctx->max_retries;

	// keep trying untill the socket is created,
	// or you run out of tries specified within the socket context
	while (retries--) {
		// create IPv4 TCP socket
		pctx->sockfd = socket(AF_INET, SOCK_STREAM, 0);
		generate_timestamp(pctx);
		
		// check if the file descriptor is valid
		if (is_valid_socket(pctx->sockfd)) {
			fprintf(stdout, "%s Socket created, socketfd->%d\n", pctx->timestamp, pctx->sockfd);
			return 1;
		}

		fprintf(stdout, "%s Invalid socketfd->%d\n", pctx->timestamp, pctx->sockfd);
	}

	// fail if all retries exhausted
	return 0;
}

// Connect to given host:port and log result
int connect_to_host(SocketContext *pctx, const char *host, int port) {
	struct addrinfo hints, *pres, *prp;

	// port number as string, max "65535"
	char port_str[6];

	// convert port to string
	snprintf(port_str, sizeof(port_str), "%d", port);

	// zero out the hints struct
	memset(&hints, 0, sizeof(hints));

	// accept only IPv4 addresses
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;

	// resolve host and port, otherwise fail
	int err = getaddrinfo(host, port_str, &hints, &pres);
	if (err != 0) {
		generate_timestamp(pctx);
		fprintf(stdout, "%s getaddrinfo: %s\n", pctx->timestamp, gai_strerror(err));
		return 0;
	}

	// attempt to iterate trough the list of resolved addresses
	// and try to connect to the socket
	int connected = 0;
	for (prp = pres; prp != NULL; prp = prp->ai_next) {
		if (connect(pctx->sockfd, prp->ai_addr, prp->ai_addrlen) == 0) {
			connected = 1;
			break;
		}
	}
	
	// free linked list of results
	freeaddrinfo(pres);

	// fail if buffer isnt connected
	if (!connected) {
		generate_timestamp(pctx);
		fprintf(stdout, "%s Connecting to %s:%d failed\n", pctx->timestamp, host, port);
		return 0;
	}

	generate_timestamp(pctx);
	fprintf(stdout, "%s Connected to %s:%d\n", pctx->timestamp, host, port);
	return 1;
}


// send buffer data via connected socket
int send_buff(SocketContext *pctx, const char *buffer) {
	// validate buffer data, if the buffer isnt valid fail
	// TODO: Allow buffers that are divisible by BUFFER_SIZE ??
	if (!is_valid_buffer(buffer)) {
		generate_timestamp(pctx);
		fprintf(stdout, "%s Invalid buffer provided !", pctx->timestamp);
		return 0;
	}

	// calculate size of buffer
	size_t num_of_bytes = strlen(buffer);

	// attempt to send buffer
	ssize_t res = send(pctx->sockfd, buffer, num_of_bytes, 0);
	if (res < 0) {
		generate_timestamp(pctx);
		fprintf(stdout, "%s Failed to send data: %s\n", pctx->timestamp, strerror(errno));
		return 0;
	}

	return 1;
}

// TODO: Add support returning data
// process incoming buffer
ssize_t recv_buff(SocketContext *pctx, char *pout_buffer, size_t buffer_size) {
	if (buffer_size <= 0) {
		// buffer is too small, to recieve any data	
		return -1;
	}

	int bytes_received = 0; 

	// get data from socket
	// allow up to BUFFER_SIZE-1 for terminator
	bytes_received = recv(pctx->sockfd, pout_buffer, buffer_size - 1, 0);
	if (bytes_received < 0) {
		generate_timestamp(pctx);
		fprintf(stdout, "%s recv failed !",pctx->timestamp);
		return -1;
	}

	// append terminator to end of buffer
	// print buffer
	pout_buffer[bytes_received] = '\0';
	generate_timestamp(pctx);
	fprintf(stdout, "%s MSG: %s", pctx->timestamp, pout_buffer);

	// return the size of received buffer
	return bytes_received;
}


#endif

