class TwinChecker:
    @staticmethod
    def check_for_close_twins(word: str, index: int):
        N = len(word)
    
        # L is length of potential twin
        for L in range(1, N // 2 + 1):
            twin_length = 2 * L
            
            start_min = max(0, index - twin_length + 1)
            start_max = min(index, N - twin_length)
            
            for start in range(start_min, start_max + 1):
                left_half = word[start : start + L]
                right_half = word[start + L : start + twin_length]
                
                if left_half == right_half:
                    return True