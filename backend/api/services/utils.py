def calculate_track_score(track_chunks):
    base_score = track_chunks[0]["score"]
    bonus = (len(track_chunks) - 1) * 0.05
    return min(base_score + bonus, 1)

def group_chunks_by_track(data, n):
    from collections import defaultdict
    result = []
    track_groups = defaultdict(list)
    
    for item in data:
        track_groups[item["track_id"]].append(item)

    for track_id, chunks in track_groups.items():
        score = calculate_track_score(chunks)
        result.append({"track_id": track_id, "score": score, "chunks": chunks})
    
    return sorted(result, key=lambda x: x["score"], reverse=True)[:n]
