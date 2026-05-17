import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_dataset_preview():
    # Set up paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'data', 'personal_carbon_footprint_behavior.csv')
    output_path = os.path.join(current_dir, 'dataset_preview.png')
    
    # Load actual dataset
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        # Select first 6 rows for preview
        preview_data = df.head(6)
    else:
        # Fallback raw data if file not found (exact first 6 rows of actual dataset)
        preview_data = pd.DataFrame({
            'transport_mode': ['EV', 'Walk', 'Walk', 'Walk', 'Walk', 'EV'],
            'electricity_kwh': [6.12, 4.50, 2.81, 10.16, 5.02, 5.14],
            'food_type': ['Non-Veg', 'Mixed', 'Mixed', 'Mixed', 'Mixed', 'Veg'],
            'carbon_footprint_kg': [11.03, 7.44, 6.01, 12.70, 6.33, 4.89]
        })
        
    # Map actual columns to template header names
    # Column mapping:
    # transport_mode -> Transport
    # electricity_kwh -> Energy (kWh)
    # food_type -> Diet
    # carbon_footprint_kg -> CF Score (kg)
    table_data = []
    for idx, row in preview_data.iterrows():
        table_data.append([
            str(row['transport_mode']),
            f"{row['electricity_kwh']:.2f} kWh",
            str(row['food_type']),
            f"{row['carbon_footprint_kg']:.2f}"
        ])
        
    headers = ["Transport", "Energy", "Diet", "CF Score"]
    
    # Create matplotlib figure with premium styling matching user's templates
    fig, ax = plt.subplots(figsize=(7.5, 3.8), facecolor='#ffffff')
    plt.subplots_adjust(top=0.82, bottom=0.08, left=0.04, right=0.96)
    
    # Hide all axis lines
    ax.axis('off')
    
    # Draw Outer Border Card Wrapper
    border_rect = patches.Rectangle((0.02, 0.03), 0.96, 0.94, transform=fig.transFigure,
                                    facecolor='#ffffff', edgecolor='#e2e8f0', linewidth=1.5, zorder=1)
    fig.patches.append(border_rect)
    
    # Card Header Label Text
    fig.text(0.06, 0.88, "Dataset Preview", color='#071d37', weight='bold', size=13, zorder=10)
    
    # Render Table
    col_widths = [0.24, 0.26, 0.26, 0.24]
    
    # Header styling properties
    header_color = '#071d37'
    header_text_color = '#ffffff'
    
    # Alternating row colors
    row_colors = ['#ffffff', '#f8f9fa']
    border_color = '#e2e8f0'
    
    # Y starting coordinate for table
    y_start = 0.72
    row_height = 0.10
    
    # Draw Table Header
    x_pos = 0.05
    for i, h in enumerate(headers):
        # Header background box
        hdr_rect = patches.Rectangle((x_pos, y_start), col_widths[i], row_height, transform=fig.transFigure,
                                     facecolor=header_color, edgecolor=border_color, linewidth=1, zorder=5)
        fig.patches.append(hdr_rect)
        
        # Header text
        fig.text(x_pos + col_widths[i]/2.0, y_start + row_height/2.0, h, color=header_text_color,
                 weight='bold', size=10, ha='center', va='center', zorder=6)
        x_pos += col_widths[i]
        
    # Draw Rows
    for row_idx, row_values in enumerate(table_data):
        y_pos = y_start - (row_idx + 1) * row_height
        x_pos = 0.05
        bg_color = row_colors[row_idx % 2]
        
        for col_idx, val in enumerate(row_values):
            # Row Cell background box
            cell_rect = patches.Rectangle((x_pos, y_pos), col_widths[col_idx], row_height, transform=fig.transFigure,
                                          facecolor=bg_color, edgecolor=border_color, linewidth=1, zorder=5)
            fig.patches.append(cell_rect)
            
            # Cell text
            fig.text(x_pos + col_widths[col_idx]/2.0, y_pos + row_height/2.0, val, color='#333333',
                     weight='medium', size=9.5, ha='center', va='center', zorder=6)
            x_pos += col_widths[col_idx]
            
    # Save the output image
    plt.savefig(output_path, dpi=300, facecolor='#ffffff')
    plt.close()
    print("Dataset Preview table infographic successfully generated.")

if __name__ == "__main__":
    generate_dataset_preview()
