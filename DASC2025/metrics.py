import pandas as pd
import numpy as np
import torch, json

jsonfile  = "max_scores_details_20250505_224334.json"
discretization = 1000

def extract_data(filename):
    with open(filename, "r") as f:
        extracted_data = json.load(f)

    data_set = dict()
    for entry in extracted_data:
        data_set.update({entry["scenario"]: {'vertiports': torch.tensor([[v["x"], v["y"]] for v in entry["vertiports"]], dtype=torch.float32).unsqueeze(0),
                                            'obstacles': torch.tensor([[v["x"], v["y"], v["radius"]] for v in entry["obstacles"]], dtype=torch.float32).unsqueeze(0),
                                            'control_points': torch.tensor(entry['control_points'], dtype=torch.float32).unsqueeze(0)}})

    return data_set

def main(jsonfile, discretization):
    data = extract_data(jsonfile)
    metrics = dict()
    for scenario, values in data.items():
        vertiport, obstacle, set_control_points = values['vertiports'], values['obstacles'], values['control_points']
        #print(f'')
        #print(f'vertiport: {vertiport}')
        #print(f'obstacle: {obstacle}')
        #print(f'set_control_points: {set_control_points}')
        metric = get_metrics(vertiport, obstacle, set_control_points, discretization)
        #print(f'metric; {metric}')
        metrics.update({scenario: metric})
    save_metrics_csv(metrics)


import pandas as pd
import numpy as np

def save_metrics_csv(metrics):
    rows = []
    for key, data in metrics.items():
        row = {'scenario': key,
            'vertiports': data['vertiports'],
            'obstacles': data['obstacles'],
            'obstacle violations': data['obstacle violations'].item(),
            'corridor_length': data['corridor length'].item(),
            'extra_flown_SF_average': data['extra-flown distance']['SF']['average'].item()}

        for i, val in enumerate(data['transitions']['average']):
            row[f'transitions_average_{i}'] = val.item()
        for i, val in enumerate(data['transitions']['cumulative']):
            row[f'transitions_cumulative_{i}'] = val.item()
        for i, val in enumerate(data['transitions']['maximum']):
            row[f'transitions_maximum_{i}'] = val.item()
        for i, val in enumerate(data['operation_length']['average']):
            row[f'operation_length_average_{i}'] = val.item()
        for i, val in enumerate(data['operation_length']['cumulative']):
            row[f'operation_length_cumulative_{i}'] = val.item()
        for i, val in enumerate(data['operation_length']['maximum']):
            row[f'operation_length_maximum_{i}'] = val.item()
        for i, val in enumerate(data['unexploited_regions']):
            row[f'unexploited_regions_{i}'] = val.item()
        for i, val in enumerate(data['extra-flown distance']['SF']['>100']):
            row[f'extra_flown_SF_over_100_{i}'] = val.item()
        for i, val in enumerate(data['extra-flown distance']['SF']['<100']):
            row[f'extra_flown_SF_under_100_{i}'] = val.item()
        for i, val in enumerate(data['extra-flown distance']['SF']['<65']):
            row[f'extra_flown_SF_under_65_{i}'] = val.item()
        for i, val in enumerate(data['extra-flown distance']['SF']['<50']):
            row[f'extra_flown_SF_under_50_{i}'] = val.item()
        for i, val in enumerate(data['extra-flown distance']['SF']['<30']):
            row[f'extra_flown_SF_under_30_{i}'] = val.item()

        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv("metrics_SMA.csv", index=False)
    print("✅ ok")

        


def get_metrics(vertiports, obstacles, control_points, n_discret_points):

    n_vertiports, n_obstacles = vertiports.shape[1], obstacles.shape[1]

    cyclic_corridor = catmull_rom_spline(control_points, n_discret_points)
    cyclic_corridor_length = calculate_length(cyclic_corridor)

    vertiports_sep = compute_pairwise_vertiport_distances(vertiports)

    ver_delta = vertiports.unsqueeze(1) - cyclic_corridor.unsqueeze(2)
    ver_separations = torch.norm(ver_delta, dim=-1)
    transitions, transition_wpts = ver_separations.min(dim=1)

    airway_distances = compute_cyclic_path_distances(cyclic_corridor, transition_wpts)
    density_clockwise, density_counter = count_bidirectional_airway_densities(transition_wpts, cyclic_corridor)

    eye = torch.eye(n_vertiports, ).unsqueeze(0)

    pair_transitions = transitions.unsqueeze(2) + transitions.unsqueeze(1) 
    pair_transitions = pair_transitions * (1 - eye)

    operation_lengths = pair_transitions + airway_distances


    d_corridor_sf =  operation_lengths - vertiports_sep
    d_pourcentage_corridor_sf = operation_lengths / vertiports_sep
    
    combinations = n_vertiports*(n_vertiports - 1)
    sum_sf = d_corridor_sf.sum(dim=-1)/combinations
    unexploited_regions = (density_clockwise == 0) + (density_counter == 0)


    dist_obs = torch.cdist(cyclic_corridor, obstacles[:, :, :-1], p=2.)
    min_dist_obs, _ = dist_obs.min(dim=1)
    nofly_zone_incursions = torch.sum(torch.where(min_dist_obs <= obstacles[:, :, -1], 1, 0), dim=-1)

    mask_100 = (1.65 < d_pourcentage_corridor_sf) & (d_pourcentage_corridor_sf < 2)
    mask_65 = (1.50 <d_pourcentage_corridor_sf) & (d_pourcentage_corridor_sf < 1.65)
    mask_50 = (1.30 < d_pourcentage_corridor_sf) & (d_pourcentage_corridor_sf < 1.50)
    mask_30 = (1 < d_pourcentage_corridor_sf) & (d_pourcentage_corridor_sf < 1.30)
    metrics = {'vertiports': n_vertiports, 
                'obstacles': n_obstacles, 
                'obstacle violations': nofly_zone_incursions,
                'transitions': {'average': transitions.mean(dim=-1), 
                                'cumulative': transitions.sum(dim=-1), 
                                'maximum': torch.amax(transitions, dim=-1)},
                'corridor length': cyclic_corridor_length,
                'operation_length': {'average': 0.5*operation_lengths.mean(dim=(1, 2)), 
                                    'cumulative': 0.5*operation_lengths.sum(dim=(1, 2)), 
                                    'maximum': torch.amax(operation_lengths, dim=(1, 2))},
                'unexploited_regions': 0.5*unexploited_regions.sum(dim=-1)/n_discret_points,
                'extra-flown distance': {'SF': {'average': sum_sf.mean(dim=-1), 
                                                '>100': (d_pourcentage_corridor_sf > 2.).sum(dim=(1,2))/combinations,
                                                '<100': mask_100.sum(dim=(1,2))/combinations,
                                                '<65': mask_65.sum(dim=(1,2))/combinations,
                                                '<50': mask_50.sum(dim=(1,2))/combinations,
                                                '<30': mask_30.sum(dim=(1,2))/combinations}}}
    return metrics

@torch.jit.script
def interpolate_catmull_rom(t: torch.Tensor, p0: torch.Tensor, p1: torch.Tensor, p2: torch.Tensor, p3: torch.Tensor, tension: float = 0.5) -> torch.Tensor:
    B = p0.shape[0]
    T = t.shape[0]
    t_exp = t.view(1, T, 1)
    p0_exp = p0.unsqueeze(1)
    p1_exp = p1.unsqueeze(1)
    p2_exp = p2.unsqueeze(1)
    p3_exp = p3.unsqueeze(1)
    a0 = -tension * p0_exp + (2 - tension) * p1_exp + (tension - 2) * p2_exp + tension * p3_exp
    a1 = 2 * tension * p0_exp + (tension - 3) * p1_exp + (3 - 2 * tension) * p2_exp - tension * p3_exp
    a2 = -tension * p0_exp + tension * p2_exp
    a3 = p1_exp
    return ((a0 * t_exp + a1) * t_exp + a2) * t_exp + a3

@torch.jit.script
def catmull_rom_spline(control_points: torch.Tensor, num_points: int) -> torch.Tensor:
    # Generate a smooth cyclic spline without duplicate endpoints.
    B, N, _ = control_points.shape
    extended_points = torch.cat([control_points[:, -2:], control_points, control_points[:, :2]], dim=1)
    points_per_segment = num_points // N
    spline_segments = []
    # Emulate endpoint=False by generating one extra point and excluding the last.
    t_values = torch.linspace(0.0, 1.0, steps=points_per_segment + 1, 
                              dtype=control_points.dtype, device=control_points.device)[:-1]
    for i in range(1, N + 1):
        p0 = extended_points[:, i - 1, :]
        p1 = extended_points[:, i, :]
        p2 = extended_points[:, i + 1, :]
        p3 = extended_points[:, i + 2, :]
        seg = interpolate_catmull_rom(t_values, p0, p1, p2, p3)
        spline_segments.append(seg)
    spline = torch.cat(spline_segments, dim=1)
    return spline

@torch.jit.script
def calculate_length(spline: torch.Tensor) -> torch.Tensor:
    diff = spline[:, 1:, :] - spline[:, :-1, :]
    seg_length = torch.sqrt((diff ** 2).sum(dim=2) + 1e-8)
    return seg_length.sum(dim=1)

@torch.jit.script
def calculate_curvature(spline: torch.Tensor) -> torch.Tensor:

    first_point, last_point = spline[:, 0:1, :], spline[:, -1:, :]
    spline = torch.cat([last_point, spline, first_point], dim=1)

    diff = spline[:, 1:, :] - spline[:, :-1, :]
    diff2 = diff[:, 1:, :] - diff[:, :-1, :]
    dx = diff[:, :-1, 0]
    dy = diff[:, :-1, 1]
    ddx = diff2[:, :, 0]
    ddy = diff2[:, :, 1]
    numerator = torch.abs(dx * ddy - dy * ddx)
    denominator = (dx**2 + dy**2).pow(1.5) + 1e-8
    curvature = numerator / denominator
    curvature = torch.cat([curvature, curvature[:, 0].unsqueeze(1)], dim=1)

    return curvature

@torch.jit.script
def check_self_intersection_improved(spline: torch.Tensor, ds_points: int = 20) -> torch.Tensor:
    # Improved intersection detection using downsampled spline segments.
    B, S, _ = spline.shape
    # Downsample indices uniformly.
    indices = torch.linspace(0, S - 1, steps=ds_points, device=spline.device).to(torch.int64)
    dspline = spline[:, indices, :]  # shape: [B, ds_points, 2]
    num_seg = dspline.shape[1] - 1  # number of segments
    intersect = torch.zeros(B, dtype=torch.float, device=spline.device)
    # Check each pair of non-adjacent segments.
    for i in range(num_seg):
        for j in range(i + 2, num_seg):
            p1 = dspline[:, i, :]   # [B, 2]
            p2 = dspline[:, i + 1, :] # [B, 2]
            q1 = dspline[:, j, :]   # [B, 2]
            q2 = dspline[:, j + 1, :] # [B, 2]
            d1 = p2 - p1
            d2 = q2 - q1
            # Compute cross product (denom = d1 x d2).
            denom = d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]
            denom = denom + 1e-8
            r = q1 - p1
            t = (r[:, 0] * d2[:, 1] - r[:, 1] * d2[:, 0]) / denom
            u = (r[:, 0] * d1[:, 1] - r[:, 1] * d1[:, 0]) / denom
            cond = (t > 0.0) & (t < 1.0) & (u > 0.0) & (u < 1.0)
            intersect = intersect + cond.float()
    # Return 1.0 if any intersection is detected in the batch, else 0.
    return (intersect > 0).float()

@torch.jit.script
def compute_reward(spline: torch.Tensor, vertiports: torch.Tensor, obstacles: torch.Tensor, reward_weight: torch.Tensor, inefficiency: torch.Tensor, max_smoothness, max_length) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]: 

    dist_attr = torch.cdist(spline, vertiports, p=2.) 
    min_dist_attr, _ = dist_attr.min(dim=1)                

    length = calculate_length(spline)
    curvature = calculate_curvature(spline)
    l2smoothness = torch.sum((curvature[:, 1:] - curvature[:, :-1])**2, dim=-1)

    dist_obs = torch.cdist(spline, obstacles[:, :, :-1], p=2.)

    wpts_violations = dist_obs < obstacles[:, :, -1].unsqueeze(1)
    _, points, nobs = wpts_violations.shape
    wpts_violations = wpts_violations.sum(dim=(1,2))

    dist_obs = torch.cdist(spline, obstacles[:, :, :-1], p=2.)
    min_dist_obs, _ = dist_obs.min(dim=1)
    reward_obstacles = -torch.sum(torch.where(min_dist_obs <= obstacles[:, :, -1], 1, 0), dim=-1)/nobs - wpts_violations/points
    reward_vertiports = torch.mean(torch.clamp((1-min_dist_attr), -1, 1), dim=-1)
    reward_intersection = -check_self_intersection_improved(spline, ds_points=20) 
    reward_curvature =  -torch.clamp(l2smoothness, 0, 12)/12
    reward_length = -torch.clamp(length, 0, 8)/8 - inefficiency
    
    reward = torch.stack([reward_vertiports, reward_obstacles, reward_intersection, reward_curvature, reward_length], dim=-1)

    return reward*reward_weight, max_smoothness, length, max_length, wpts_violations/points

@torch.jit.script
def compute_cost(spline: torch.Tensor, vertiports: torch.Tensor, obstacles: torch.Tensor, cost_weight: torch.Tensor, efficiency: torch.Tensor, max_smoothness, max_length) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]: 

    dist_attr = torch.cdist(spline, vertiports, p=2.) 
    min_dist_attr, _ = dist_attr.min(dim=1)                

    length = calculate_length(spline)
    curvature = calculate_curvature(spline)
    l2smoothness = torch.sum((curvature[:, 1:] - curvature[:, :-1])**2, dim=-1)

    cost_curvature =  l2smoothness / max_smoothness
    cost_intersection = check_self_intersection_improved(spline, ds_points=20) 

    max_length = torch.max(length.max(), max_length)

    cost_length = length / max_length
    
    cost_vertiports = torch.zeros_like(min_dist_attr)
    cost_vertiports = torch.where(min_dist_attr <= 0.1, 0, 1.0)
    cost_vertiports = cost_vertiports.sum(dim=1) + efficiency
    
    dist_obs = torch.cdist(spline, obstacles[:, :, :-1], p=2.)
    violations = dist_obs < obstacles[:, :, -1].unsqueeze(1)
    _, points, nobs = violations.shape
    violations = violations.sum(dim=1)

    min_dist_obs, _ = dist_obs.min(dim=1)

    cost_obstacles = torch.zeros_like(min_dist_obs)
    cost_obstacles = torch.where(min_dist_obs  >= obstacles[:, :, -1], -1.0, 0) + violations/points
    cost_obstacles = cost_obstacles.sum(dim=1)

    cost = torch.cat([cost_vertiports, cost_obstacles, cost_intersection, cost_curvature, cost_length], dim=-1)

    return cost*cost_weight, length, violations.sum(dim=-1)/nobs

@torch.jit.script
def compute_pairwise_vertiport_distances(vertiports: torch.Tensor):
    diff = vertiports[:, :, None, :] - vertiports[:, None, :, :]
    dists = torch.norm(diff, dim=-1)
    return dists

import torch

@torch.jit.script
def compute_cyclic_path_distances(airway_points: torch.Tensor, transition_indices: torch.Tensor) -> torch.Tensor:
    n, k, _ = airway_points.shape
    _, m = transition_indices.shape

    next_points = torch.roll(airway_points, shifts=-1, dims=1)
    segment_lengths = torch.norm(next_points - airway_points, dim=2)  # (n, k)

    # Cumulative lengths
    cumulative_lengths = torch.cumsum(segment_lengths, dim=1)  # (n, k)
    total_lengths = cumulative_lengths[:, -1] + segment_lengths[:, -1]  # (n,)

    min_distances = torch.zeros((n, m, m), dtype=airway_points.dtype)

    for i in range(n):
        for j in range(m):
            idx_j = transition_indices[i, j]
            for l in range(m):
                if j == l:
                    continue
                idx_l = transition_indices[i, l]

                if idx_j <= idx_l:
                    clockwise = cumulative_lengths[i, idx_l] - cumulative_lengths[i, idx_j]
                else:
                    clockwise = total_lengths[i] - (cumulative_lengths[i, idx_j] - cumulative_lengths[i, idx_l])
                
                counter_clockwise = total_lengths[i] - clockwise
                min_distances[i, j, l] = torch.min(clockwise, counter_clockwise)

    return min_distances

@torch.jit.script
def count_bidirectional_airway_densities(transition_indices: torch.Tensor, corridor: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    n, m = transition_indices.shape
    k = corridor.shape[1]

    density_clockwise = torch.zeros((n, k), dtype=torch.int32)
    density_counter = torch.zeros((n, k), dtype=torch.int32)

    for i in range(n):
        for j in range(m):
            idx_j = transition_indices[i, j]
            for l in range(m):
                if j == l:
                    continue
                idx_l = transition_indices[i, l]
                if idx_j <= idx_l:
                    path_cw = torch.arange(idx_j, idx_l + 1)
                else:
                    path_cw = torch.cat((torch.arange(idx_j, k), torch.arange(0, idx_l + 1)))
                len_cw = path_cw.numel()
                if idx_l <= idx_j:
                    path_ccw = torch.arange(idx_l, idx_j + 1)
                else:
                    path_ccw = torch.cat((torch.arange(idx_l, k),torch.arange(0, idx_j + 1)))

                len_ccw = path_ccw.numel()

                if len_cw <= len_ccw:
                    for p in path_cw:
                        density_clockwise[i, p] += 1
                else:
                    for p in path_ccw:
                        density_counter[i, p] += 1

    return density_clockwise, density_counter

#main(jsonfile, discretization)

tensor = torch.tensor([[
  [43.58656633,  1.43126810],
  [43.59288334,  1.43734944],
  [43.59942843,  1.43914275],
  [43.60206177,  1.43559884],
  [43.60357295,  1.42421804]]])


corridor = catmull_rom_spline(tensor, num_points=500)
corridor = corridor.squeeze().numpy()
rows = {'latitude': corridor[:, 0],'longitude': corridor[:, 1]}
df = pd.DataFrame(rows)
df.to_csv("corridor_new.csv")