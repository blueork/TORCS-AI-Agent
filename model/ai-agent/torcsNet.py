import torch
import torch.nn as nn

# Neural Network Model
class TORCSNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_gear_classes, num_clutch_classes):
        super(TORCSNet, self).__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size),  # Third hidden layer
            nn.ReLU()
            # nn.Dropout(0.3)
        )
        self.continuous_head = nn.Linear(hidden_size, 3)
        self.gear_head = nn.Linear(hidden_size, num_gear_classes)
        self.clutch_head = nn.Linear(hidden_size, num_clutch_classes)

    def forward(self, x):
        shared_features = self.shared(x)
        continuous_out = self.continuous_head(shared_features)
        accel_brake = torch.sigmoid(continuous_out[:, :2])  # [0, 1]
        steering = torch.tanh(continuous_out[:, 2])         # [-1, 1]
        continuous_out = torch.cat([accel_brake, steering.unsqueeze(1)], dim=1)
        gear_out = self.gear_head(shared_features)
        clutch_out = self.clutch_head(shared_features)
        return continuous_out, gear_out, clutch_out