classDiagram
    class User {
        +String name
        +String password
    }

    class Video {
        +String name
        +File content1080p
        +File content720p
        +File content360p
        +File content120p
        +String status
    }

    class WatchedVideo {
        +Time watchedUntil
    }

    User "1" --> "many" WatchedVideo : watches
    Video "1" --> "1" WatchedVideo : is watched in
