#import <Foundation/Foundation.h>

#import "ObjcHelper.h"
#import "kexploit/kfs.h"

void enumerateProcessesUsingBlock(void (^enumerator)(pid_t pid, NSString* executablePath, BOOL* stop));
void killall(NSString* processName);

@implementation ObjcHelper

-(NSNumber *)getDeviceSubType {
    NSString *plistFullPath = [@"/private/var/containers/Shared/SystemGroup/systemgroup.com.apple.mobilegestaltcache/Library/Caches/" stringByAppendingPathComponent:@"com.apple.MobileGestalt.plist"];
    NSMutableDictionary *plistDict = [[NSMutableDictionary alloc] initWithContentsOfFile:plistFullPath];
    
    NSMutableDictionary *artWork = plistDict[@"CacheExtra"][@"oPeik/9e8lQWMszEjbPzng"];
    
    return artWork[@"ArtworkDeviceSubType"];
}

-(void)updateDeviceSubType:(NSInteger)deviceSubType {
    NSString *plistFullPath = [@"/private/var/containers/Shared/SystemGroup/systemgroup.com.apple.mobilegestaltcache/Library/Caches/" stringByAppendingPathComponent:@"com.apple.MobileGestalt.plist"];
    NSMutableDictionary *plistDict = [[NSMutableDictionary alloc] initWithContentsOfFile:plistFullPath];
    
    [plistDict[@"CacheExtra"][@"oPeik/9e8lQWMszEjbPzng"] setObject:[NSNumber numberWithInteger: deviceSubType] forKey:@"ArtworkDeviceSubType"];
    [plistDict writeToFile:plistFullPath atomically:YES];
}

-(void)imageToCPBitmap:(UIImage *)img path:(NSString *)path {
    [img writeToCPBitmapFile:path flags:1];
}

-(void)respring {
    killall(@"SpringBoard");
    exit(0);
}

-(void)refreshWalletServices {
    killall(@"passd");
    killall(@"walletd");
    killall(@"PassbookUIService");
    // Daemons auto-relaunch. No need to kill SpringBoard or exit.
}

-(UIImage *)getImageFromData:(NSString *)path {
    NSData *data = [NSData dataWithContentsOfFile:path];
    UIImage *image = [UIImage imageWithData:data];
    
    return image;
}

-(void)saveImage:(UIImage *)image atPath:(NSString *)path {
    [[NSFileManager defaultManager] removeItemAtPath:path error:nil];
    [UIImagePNGRepresentation(image) writeToFile:path atomically:YES];
}

-(NSArray<NSString *> *)kfsListDirectory:(NSString *)path {
    if (path.length == 0 || !kfs_can_listdir()) {
        return @[];
    }

    kfs_entry_t *entries = NULL;
    int count = 0;
    int rc = kfs_listdir(path.UTF8String, &entries, &count);
    if (rc != 0 || entries == NULL || count <= 0) {
        if (entries != NULL) {
            kfs_free_listing(entries);
        }
        return @[];
    }

    NSMutableArray<NSString *> *results = [NSMutableArray arrayWithCapacity:(NSUInteger)count];
    for (int i = 0; i < count; i++) {
        NSString *name = [NSString stringWithUTF8String:entries[i].name];
        if (name.length > 0) {
            [results addObject:name];
        }
    }

    kfs_free_listing(entries);
    return results;
}

-(int64_t)kfsFileSizeNC:(NSString *)path {
    if (path.length == 0) return -1;
    return kfs_file_size_nc(path.UTF8String);
}

-(NSData * _Nullable)kfsReadFile:(NSString *)path maxSize:(int64_t)maxSize {
    if (path.length == 0 || maxSize <= 0) return nil;

    int64_t fsize = kfs_file_size_nc(path.UTF8String);
    if (fsize <= 0) fsize = maxSize;
    if (fsize > maxSize) fsize = maxSize;

    void *buf = calloc(1, (size_t)fsize);
    if (!buf) return nil;

    int64_t n = kfs_read(path.UTF8String, buf, (size_t)fsize, 0);
    if (n <= 0) {
        free(buf);
        return nil;
    }

    NSData *data = [NSData dataWithBytes:buf length:(NSUInteger)n];
    free(buf);
    return data;
}

// MARK: - TSUtil

void enumerateProcessesUsingBlock(void (^enumerator)(pid_t pid, NSString* executablePath, BOOL* stop)) {
    static int maxArgumentSize = 0;
    if (maxArgumentSize == 0) {
        size_t size = sizeof(maxArgumentSize);
        if (sysctl((int[]){ CTL_KERN, KERN_ARGMAX }, 2, &maxArgumentSize, &size, NULL, 0) == -1) {
            perror("sysctl argument size");
            maxArgumentSize = 4096; // Default
        }
    }
    int mib[3] = { CTL_KERN, KERN_PROC, KERN_PROC_ALL};
    struct kinfo_proc *info;
    size_t length;
    int count;
    
    if (sysctl(mib, 3, NULL, &length, NULL, 0) < 0)
        return;
    if (!(info = malloc(length)))
        return;
    if (sysctl(mib, 3, info, &length, NULL, 0) < 0) {
        free(info);
        return;
    }
    count = length / sizeof(struct kinfo_proc);
    for (int i = 0; i < count; i++) {
        @autoreleasepool {
        pid_t pid = info[i].kp_proc.p_pid;
        if (pid == 0) {
            continue;
        }
        size_t size = maxArgumentSize;
        char* buffer = (char *)malloc(length);
        if (sysctl((int[]){ CTL_KERN, KERN_PROCARGS2, pid }, 3, buffer, &size, NULL, 0) == 0) {
            NSString* executablePath = [NSString stringWithCString:(buffer+sizeof(int)) encoding:NSUTF8StringEncoding];
            
            BOOL stop = NO;
            enumerator(pid, executablePath, &stop);
            if(stop) {
                free(buffer);
                break;
            }
        }
        free(buffer);
        }
    }
    free(info);
}

void killall(NSString* processName) {
    enumerateProcessesUsingBlock(^(pid_t pid, NSString* executablePath, BOOL* stop) {
        if([executablePath.lastPathComponent isEqualToString:processName]) {
            kill(pid, SIGTERM);
        }
    });
}
@end
