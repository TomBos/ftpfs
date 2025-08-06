#ifndef SOCK_UTILS_H
#define SOCK_UTILS_H

#include <time.h>
#include <sys/time.h>
#include <sys/socket.h>

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
	return -1;
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
		return -1;
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

	if (!connected) {
		generate_timestamp(pctx);
		fprintf(stdout, "%s Connecting to %s:%d failed\n", pctx->timestamp, host, port);
		return -1;
	}

	generate_timestamp(pctx);
	fprintf(stdout, "%s Connected to %s:%d\n", pctx->timestamp, host, port);
	return 1;
}

#endif

