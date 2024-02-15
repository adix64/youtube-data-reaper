import os
import googleapiclient.discovery
import googleapiclient.errors

def get_video_statistics(youtube, video_id):
    video_request = youtube.videos().list(
        part="statistics",
        id=video_id
    )
    video_response = video_request.execute()
    return video_response['items'][0]['statistics']

def get_channel_statistics(youtube, channel_id):
    channel_request = youtube.channels().list(
        part="statistics",
        id=channel_id
    )
    channel_response = channel_request.execute()
    return channel_response['items'][0]['statistics']

def main():
    api_key = "AIzaSyA46ehaE6ov71md0No8ZfIjfWFB4z-X4h8"
    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

    request = youtube.search().list(
        part="snippet",
        maxResults=32,
        q="draw Batman"#,
     #   order="viewCount"
    )
    response = request.execute()

    videos_data = []

    for item in response['items']:
        video_id = item['id']['videoId']
        channel_id = item['snippet']['channelId']

        video_stats = get_video_statistics(youtube, video_id)
        channel_stats = get_channel_statistics(youtube, channel_id)

        videos_data.append({
            'videoId': video_id,
            'viewCount': int(video_stats.get('viewCount', 0)),  # Convert viewCount to int for sorting
            'likeCount': video_stats.get('likeCount'),
            'channelId': channel_id,
            'subscriberCount': channel_stats.get('subscriberCount')
        })

    # Sort videos by viewCount in descending order
    sorted_videos = sorted(videos_data, key=lambda x: int(x['likeCount'] or 0), reverse=True)

    for video in sorted_videos:
        print(video)
        video_id = video['videoId']
        print(f"\t\t\thttps://www.youtube.com/watch?v={video_id}")


if __name__ == "__main__":
    main()
