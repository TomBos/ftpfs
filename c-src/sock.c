#include <stdio.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

void generate_timestamp(char *out, size_t size) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    if (!t) return;
    strftime(out, size, "[%d.%m.%Y %H:%M:%S]", t);
}

int socket_valid(int sockfd) {
    // 0 stdin, 1 stdout, 2 stderr
    // these are common unix file descriptors
    // they may be used but they probably wont be
    return sockfd >= 0;
}

int create_tcp_socket(int max_tries) {
    char time_stamp[32];
    int sockfd;

    while (max_tries--) {
        sockfd = socket(AF_INET, SOCK_STREAM, 0);
        generate_timestamp(time_stamp, sizeof(time_stamp));

        if (socket_valid(sockfd)) {
            printf("%s Socket created, socketfd->%d\n", time_stamp, sockfd);
            return sockfd;
        }

        printf("%s Invalid socketfd->%d\n", time_stamp, sockfd);
    }

    return -1;
}

int main() {
    int sockfd = create_tcp_socket(3);
    if (sockfd < 0) {
        fprintf(stderr, "Failed to create socket after retries\n");
        return 1;
    }


    close(sockfd);
    return 0;
}

