import os
import argparse
import csv
from voiceprint import extract_features, compare_features


def collect_dataset(dataset_dir):
    # Expect structure: dataset/<speaker>/*.wav
    speakers = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d))]
    data = {}
    for sp in speakers:
        spath = os.path.join(dataset_dir, sp)
        wavs = [os.path.join(spath, f) for f in os.listdir(spath) if f.lower().endswith(('.wav', '.flac'))]
        wavs.sort()
        if wavs:
            data[sp] = wavs
    return data


def enroll(data):
    # Use first file per speaker as enrollment
    enrollments = {}
    for sp, files in data.items():
        feat = extract_features(files[0])
        enrollments[sp] = feat
    return enrollments


def evaluate(dataset_dir, out_csv='evaluation_results.csv'):
    data = collect_dataset(dataset_dir)
    if not data:
        print('No dataset found at', dataset_dir)
        return

    enrollments = enroll(data)

    rows = []
    total = 0
    correct = 0

    for sp, files in data.items():
        # use remaining files as probes
        probes = files[1:] if len(files) > 1 else []
        for p in probes:
            total += 1
            probe_feat = extract_features(p)
            best_score = -1
            best_sp = None
            best_details = None
            for esp, efeat in enrollments.items():
                res = compare_features(probe_feat, efeat)
                if res['score'] > best_score:
                    best_score = res['score']
                    best_sp = esp
                    best_details = res

            is_correct = (best_sp == sp)
            if is_correct:
                correct += 1
            rows.append({
                'probe': p,
                'true_speaker': sp,
                'predicted': best_sp,
                'score': best_score,
                'dtw_cost': best_details['dtw_cost'],
                'cos_sim': best_details['cos_sim'],
                'peak_corr': best_details['peak_corr'],
                'correct': is_correct
            })

    acc = (correct / total) if total > 0 else 0.0
    # write CSV
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['probe', 'true_speaker', 'predicted', 'score', 'dtw_cost', 'cos_sim', 'peak_corr', 'correct'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print('Evaluation finished')
    print(f'Total probes: {total}, Correct: {correct}, Accuracy: {acc:.4f}')
    print('Results saved to', out_csv)


def main():
    parser = argparse.ArgumentParser(description='Evaluate local voiceprint system')
    parser.add_argument('--dataset', '-d', required=True, help='Path to dataset folder (dataset/<speaker>/*.wav)')
    parser.add_argument('--out', '-o', default='evaluation_results.csv', help='Output CSV file')
    args = parser.parse_args()
    evaluate(args.dataset, args.out)


if __name__ == '__main__':
    main()
