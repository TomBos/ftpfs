#ifndef STRUCTS_H
#define STRUCTS_H

// Holds socket info and metadata
typedef struct {
    int sockfd;             // file descriptor for the socket
    int max_retries;        // how many times to retry socket creation
    char timestamp[32];     // human-readable timestamp (log last action)
} SocketContext;

#endif

