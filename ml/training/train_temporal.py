"""Train the temporal model from supplied measured feature windows and future labels."""
import argparse
import numpy as np
import torch
from ml.models.temporal_model import TemporalForecaster


def main():
    parser = argparse.ArgumentParser(description="Train NPZ X[N,T,D], y_10s/y_30s/y_1m/y_5m[N] with zero-based future class indices")
    parser.add_argument("--data", required=True)
    parser.add_argument("--num-classes", required=True, type=int)
    parser.add_argument("--epochs", default=5, type=int)
    parser.add_argument("--output", default="temporal_model.pt")
    args = parser.parse_args()
    horizons = ("10s", "30s", "1m", "5m")
    with np.load(args.data, allow_pickle=False) as data:
        X = torch.as_tensor(data["X"], dtype=torch.float32)
        labels = [torch.as_tensor(data["y_" + h], dtype=torch.long) for h in horizons]
    if X.ndim != 3 or not len(X) or not X.shape[1] or not X.shape[2] or not torch.isfinite(X).all():
        parser.error("Expected finite nonempty X[N,T,D]")
    if args.epochs < 1 or args.num_classes < 2 or any(y.shape != (len(X),) or y.min() < 0 or y.max() >= args.num_classes for y in labels):
        parser.error("Invalid future labels, class count, or epoch count")
    torch.manual_seed(42)
    model = TemporalForecaster(X.shape[2], args.num_classes)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.CrossEntropyLoss()
    loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(X, *labels), batch_size=64, shuffle=False)
    for epoch in range(args.epochs):
        model.train()
        losses = []
        for batch in loader:
            optimizer.zero_grad()
            predictions = model(batch[0])
            loss = sum(criterion(predictions[h], batch[i+1]) for i, h in enumerate(horizons))
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
        print(f"Epoch {epoch+1}: training loss {np.mean(losses):.6f}")
    model.save(args.output)
    print(f"Saved {args.output}; no held-out performance claim is made.")


if __name__ == "__main__":
    main()
