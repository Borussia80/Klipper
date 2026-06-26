module Api
  module V1
    class CategoriesController < BaseController
      before_action :set_category, only: %i[show update destroy]

      def index
        categories = current_user.categories.active.order(:name)
        render json: categories
      end

      def show
        render json: @category
      end

      def create
        category = current_user.categories.build(category_params)
        if category.save
          render json: category, status: :created
        else
          render json: { errors: category.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def update
        if @category.update(category_params)
          render json: @category
        else
          render json: { errors: @category.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def destroy
        @category.update!(active: false)
        head :no_content
      end

      private

      def set_category
        @category = current_user.categories.find(params[:id])
      rescue ActiveRecord::RecordNotFound
        render_error("Categoria não encontrada", status: :not_found)
      end

      def category_params
        params.permit(:name, :icon, :category_type, :color)
      end
    end
  end
end
