import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import io

class PivotVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Pivot Visualizer")
        self.root.geometry("1000x700")
        
        # Khởi tạo dữ liệu
        self.df = None
        self.pivot_df = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame chính
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame cho input data
        input_frame = ttk.LabelFrame(main_frame, text="Dữ liệu đầu vào", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tạo 4 ô input cho 4 cột
        self.create_input_fields(input_frame)
        
        # Frame cho filter và buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Filter cho md_position
        filter_frame = ttk.LabelFrame(control_frame, text="Filter md_position", padding=5)
        filter_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.filter_var = tk.StringVar()
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                        state="readonly", width=15)
        self.filter_combo.pack()
        self.filter_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Tạo Pivot", command=self.create_pivot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Vẽ đường tròn", command=self.draw_circle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Xóa dữ liệu", command=self.clear_data).pack(side=tk.LEFT, padx=5)
        
        # Frame cho kết quả
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview để hiển thị pivot table
        self.setup_treeview(result_frame)
        
        # Canvas cho matplotlib
        self.setup_matplotlib(result_frame)
        
    def create_input_fields(self, parent):
        # Frame cho labels
        label_frame = ttk.Frame(parent)
        label_frame.pack(fill=tk.X, pady=(0, 5))
        
        labels = ["x_Rows", "y_Columns", "CA_1", "md_position"]
        for i, label in enumerate(labels):
            ttk.Label(label_frame, text=label, width=15).grid(row=0, column=i, padx=5)
        
        # Frame cho text widgets
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_widgets = []
        for i in range(4):
            text_widget = tk.Text(text_frame, height=8, width=15)
            text_widget.grid(row=0, column=i, padx=5, sticky="nsew")
            self.text_widgets.append(text_widget)
            
        # Configure grid weights
        for i in range(4):
            text_frame.columnconfigure(i, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
    def setup_treeview(self, parent):
        # Frame cho treeview
        tree_frame = ttk.LabelFrame(parent, text="Pivot Table", padding=5)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Treeview với scrollbars
        tree_container = ttk.Frame(tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_container)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars và treeview
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_matplotlib(self, parent):
        # Frame cho matplotlib
        plot_frame = ttk.LabelFrame(parent, text="Visualization", padding=5)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Tạo figure
        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def parse_input_data(self):
        try:
            # Lấy dữ liệu từ 4 text widgets
            columns_data = []
            column_names = ["x_Rows", "y_Columns", "CA_1", "md_position"]
            
            for i, text_widget in enumerate(self.text_widgets):
                data = text_widget.get("1.0", tk.END).strip()
                if not data:
                    messagebox.showerror("Lỗi", f"Vui lòng nhập dữ liệu cho cột {column_names[i]}")
                    return None
                
                # Tách dữ liệu theo dòng
                lines = [line.strip() for line in data.split('\n') if line.strip()]
                columns_data.append(lines)
            
            # Kiểm tra độ dài các cột
            lengths = [len(col) for col in columns_data]
            if len(set(lengths)) > 1:
                messagebox.showerror("Lỗi", "Các cột phải có cùng số lượng dòng dữ liệu")
                return None
            
            # Tạo DataFrame
            data_dict = {}
            for i, col_name in enumerate(column_names):
                if col_name == "CA_1":
                    # Chuyển đổi CA_1 thành số
                    try:
                        data_dict[col_name] = [float(x) for x in columns_data[i]]
                    except ValueError:
                        messagebox.showerror("Lỗi", "Cột CA_1 phải chứa các giá trị số")
                        return None
                else:
                    data_dict[col_name] = columns_data[i]
            
            self.df = pd.DataFrame(data_dict)
            
            # Cập nhật filter combo
            unique_positions = sorted(self.df['md_position'].unique())
            self.filter_combo['values'] = ['Tất cả'] + unique_positions
            self.filter_combo.set('Tất cả')
            
            return self.df
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi xử lý dữ liệu: {str(e)}")
            return None
    
    def create_pivot(self):
        if self.parse_input_data() is None:
            return
        
        try:
            # Lọc dữ liệu theo filter
            filtered_df = self.get_filtered_data()
            
            # Tạo pivot table
            self.pivot_df = filtered_df.pivot_table(
                index='x_Rows',
                columns='y_Columns', 
                values='CA_1',
                aggfunc='sum',
                fill_value=0
            )
            
            # Hiển thị trong treeview
            self.display_pivot_table()
            
            messagebox.showinfo("Thành công", "Đã tạo pivot table thành công!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi tạo pivot table: {str(e)}")
    
    def get_filtered_data(self):
        if self.df is None:
            return None
        
        filter_value = self.filter_var.get()
        if filter_value == 'Tất cả' or filter_value == '':
            return self.df
        else:
            return self.df[self.df['md_position'] == filter_value]
    
    def display_pivot_table(self):
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.pivot_df is None:
            return
        
        # Thiết lập columns
        columns = ['Index'] + list(self.pivot_df.columns)
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        # Thiết lập headers
        for col in columns:
            self.tree.heading(col, text=str(col))
            self.tree.column(col, width=80)
        
        # Thêm dữ liệu
        for index, row in self.pivot_df.iterrows():
            values = [str(index)] + [str(val) for val in row.values]
            self.tree.insert('', tk.END, values=values)
    
    def on_filter_change(self, event=None):
        if self.df is not None:
            self.create_pivot()
    
    def draw_circle(self):
        if self.pivot_df is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng tạo pivot table trước!")
            return
        
        try:
            # Xóa plot cũ
            self.ax.clear()
            
            # Lấy tọa độ X, Y từ pivot table
            x_coords = []
            y_coords = []
            
            for x_idx, x_val in enumerate(self.pivot_df.index):
                for y_idx, y_val in enumerate(self.pivot_df.columns):
                    if self.pivot_df.iloc[x_idx, y_idx] != 0:  # Chỉ lấy các điểm có giá trị
                        try:
                            x_coords.append(float(x_val))
                            y_coords.append(float(y_val))
                        except ValueError:
                            # Nếu không thể chuyển đổi thành số, sử dụng index
                            x_coords.append(x_idx)
                            y_coords.append(y_idx)
            
            if not x_coords or not y_coords:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu để vẽ!")
                return
            
            # Vẽ các điểm
            self.ax.scatter(x_coords, y_coords, c='red', s=50, alpha=0.7, label='Data Points')
            
            # Tính toán đường tròn ngoại tiếp
            if len(x_coords) >= 3:
                center_x = np.mean(x_coords)
                center_y = np.mean(y_coords)
                
                # Tính bán kính (khoảng cách xa nhất từ tâm)
                distances = [np.sqrt((x - center_x)**2 + (y - center_y)**2) 
                           for x, y in zip(x_coords, y_coords)]
                radius = max(distances)
                
                # Vẽ đường tròn
                circle = Circle((center_x, center_y), radius, fill=False, 
                              color='blue', linewidth=2, label=f'Circle (r={radius:.2f})')
                self.ax.add_patch(circle)
                
                # Vẽ tâm
                self.ax.plot(center_x, center_y, 'bo', markersize=8, label='Center')
                
            # Thiết lập plot
            self.ax.set_xlabel('X (x_Rows)')
            self.ax.set_ylabel('Y (y_Columns)')
            self.ax.set_title('Data Points with Circumscribed Circle')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            self.ax.set_aspect('equal', adjustable='box')
            
            # Refresh canvas
            self.canvas.draw()
            
            messagebox.showinfo("Thành công", "Đã vẽ đường tròn ngoại tiếp thành công!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi vẽ đường tròn: {str(e)}")
    
    def clear_data(self):
        # Xóa dữ liệu trong text widgets
        for text_widget in self.text_widgets:
            text_widget.delete("1.0", tk.END)
        
        # Xóa treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Xóa plot
        self.ax.clear()
        self.canvas.draw()
        
        # Reset variables
        self.df = None
        self.pivot_df = None
        self.filter_combo['values'] = []
        self.filter_combo.set('')
        
        messagebox.showinfo("Thành công", "Đã xóa tất cả dữ liệu!")

def main():
    root = tk.Tk()
    app = PivotVisualizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
